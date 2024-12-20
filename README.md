---
title: S1
emoji: 🐠
colorFrom: gray
colorTo: indigo
sdk: gradio
sdk_version: 5.4.0
app_file: app.py
pinned: false
short_description: test of GPU accelerated Milvus setup
---

# S1

This is a practise of a simple RAG chatbot that allows upload of file then conduct Q&A using NVIDIA NIM.  It's orchestrated by LlamaIndex and GPU-accelerated Milvus Vector Store, using NVIDIA embeddings. 

## Setup

1. Clone the repository:
```
git clone https://github.com/142CodeGreen/S1.git
cd S1
```

2. Install the required packages:
```
pip install --upgrade -r requirements.txt
```

3. Export API keys. NVIDIA_API_KEY is for NVIDIA NIM, while OpenAI API Key is needed for Nemo Guardrails. 
```
export NVIDIA_API_KEY="your-api-key-here"
echo $NVIDIA_API_KEY

```

4. Run the app.py:
```
python3 app.py
```

## Optional: use GPU-accelerated Milvus container:

1. Refer this [tutorial](https://milvus.io/docs/install_standalone-docker-compose-gpu.md) to install required environments for GPU-accelerated Milvus container, including:
   - Docker
   - NVIDIA Docker container tool kit & NVIDIA Driver

To utilize GPU acceleration in the vector database, ensure that:
- Your system has a compatible NVIDIA GPU.
- You're using the GPU-enabled version of Milvus (as shown in the step 2 below).
- There are enough concurrent requests to justify GPU usage. GPU acceleration typically shows significant benefits under high load conditions.

2. It's important to note that GPU acceleration will only be used when the incoming requests are extremely high. For more detailed information on GPU indexing and search in Milvus, refer to the [official Milvus GPU Index documentation](https://milvus.io/docs/gpu_index.md).

To connect the GPU-accelerated Milvus with LlamaIndex, update the MilvusVectorStore configuration in app.py:

```
vector_store = MilvusVectorStore(
    host="127.0.0.1",
    port=19530,
    dim=1024,
    collection_name="your_collection_name",
    gpu_id=0,  # Specify the GPU ID to use
    output_fields=["field1","field2"]
)
```
     
3. Upon above environment set up, start the GPU-accelerated Milvus container:
```
sudo docker compose up -d
```

4. Ensure the Milvus container is running:

```
docker ps
```

5. Run the app.py:
```
python3 -m S1.app
```

- Open the provided URL in your web browser.

- Upload PDF file librarie and set up the environment context.

- Process the files by clicking the "Upload PDF" button.

- Once processing is complete, use the chat interface to query your documents.
