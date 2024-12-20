import torch
import os
import gradio as gr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.llms.nvidia import NVIDIA
Settings.llm = NVIDIA(model="meta/llama-3.1-8b-instruct")

from llama_index.embeddings.nvidia import NVIDIAEmbedding
Settings.embed_model = NVIDIAEmbedding(model="NV-Embed-QA", truncate="END")

from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core.node_parser import SentenceSplitter
Settings.text_splitter = SentenceSplitter(chunk_size=400)

# Ensure GPU usage
if torch.cuda.is_available():
    logger.info("GPU is available and will be used.")
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Assuming you want to use GPU 0
else:
    logger.warning("GPU not detected or not configured correctly. Falling back to CPU.")

index = None
query_engine = None

# Function to get file names from file objects
def get_files_from_input(file_objs):
    if not file_objs:
        return []
    return [file_obj.name for file_obj in file_objs]

# Function to load documents and create the index
def load_documents(file_objs):
    global index, query_engine
    try:
        if not file_objs:
            return "Error: No files selected."

        file_paths = get_files_from_input(file_objs)
        documents = []
        for file_path in file_paths:
            directory = os.path.dirname(file_path)
            documents.extend(SimpleDirectoryReader(input_files=[file_path]).load_data())

        if not documents:
            return f"No documents found in the selected files."

        # Create a Milvus vector store and storage context
        vector_store = MilvusVectorStore(
            host="127.0.0.1",
            port=19530,
            dim=1024,
            collection_name="your_collection_name",
            gpu_id=0  # Specify the GPU ID to use
        )
            #output_fields=["field1","field2"]
    
        
        #vector_store = MilvusVectorStore(uri="./milvus_demo.db", dim=1024, overwrite=True,output_fields=[])  # use CPU
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create the index from the documents
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context) # Create index inside the function after documents are loaded

        # Create the query engine after the index is created
        query_engine = index.as_query_engine(similarity_top_k=20, streaming=True)
        return f"Successfully loaded {len(documents)} documents from {len(file_paths)} files."
    except Exception as e:
        return f"Error loading documents: {str(e)}"

# Function to handle chat interactions
def chat(message,history):
    global query_engine
    if query_engine is None:
        return history + [("Please upload a file first.",None)]
    try:
        response = query_engine.query(message)
        return history + [(message,response)]
    except Exception as e:
        return history + [(message,f"Error processing query: {str(e)}")]

# Function to stream responses
def stream_response(message,history):
    global query_engine
    if query_engine is None:
        yield history + [("Please upload a file first.",None)]
        return

    try:
        response = query_engine.query(message)
        partial_response = ""
        for text in response.response_gen:
            partial_response += text
            yield history + [(message, partial_response)]
    except Exception as e:
        yield history + [(message, f"Error processing query: {str(e)}")]

# Create the Gradio interface
with gr.Blocks() as demo:
  gr.Markdown("# RAG Chatbot")

  with gr.Row():
      file_input = gr.File(label="Select files to upload", file_count="multiple")
      load_btn = gr.Button("Load Documents")

  load_output = gr.Textbox(label="Load Status")

  chatbot = gr.Chatbot()
  msg = gr.Textbox(label="Enter your question",interactive=True)
  clear = gr.Button("Clear")

# Set up event handler (Event handlers should be defined within the 'with gr.Blocks() as demo:' block)
  load_btn.click(load_documents, inputs=[file_input], outputs=[load_output])
  msg.submit(stream_response, inputs=[msg, chatbot], outputs=[chatbot]) # Use submit button instead of msg
  clear.click(lambda: None, None, chatbot, queue=False)

# Launch the Gradio interface
if __name__ == "__main__":
    demo.queue().launch(share=True,debug=True)
