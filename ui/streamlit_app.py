"""Streamlit UI for Enterprise Knowledge Assistant"""
import streamlit as st
import requests
import time
from typing import List

# Page configuration
st.set_page_config(
    page_title="Enterprise Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .element-container {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"


@st.cache_resource
def get_api_client():
    """Create API client"""
    return requests.Session()


def upload_pdf(file) -> bool:
    """Upload PDF file to backend"""
    try:
        files = {"file": file}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)

        if response.status_code == 200:
            st.success(f"✅ File uploaded successfully!")
            data = response.json()
            st.info(f"Document ID: {data['document_id']}\n{data['message']}")
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"❌ Upload failed: {error_detail}")
            return False

    except Exception as e:
        st.error(f"❌ Error uploading file: {str(e)}")
        return False


def ask_question(question: str, top_k: int = 5) -> dict:
    """Send question to backend"""
    try:
        payload = {
            "question": question,
            "top_k": top_k,
            "include_sources": True,
        }

        response = requests.post(f"{API_BASE_URL}/ask", json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            return None

    except Exception as e:
        st.error(f"Error asking question: {str(e)}")
        return None


def list_documents() -> List[dict]:
    """Get list of documents"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents?limit=100")

        if response.status_code == 200:
            return response.json().get("documents", [])
        else:
            return []

    except Exception as e:
        st.error(f"Error retrieving documents: {str(e)}")
        return []


def delete_document(document_id: int) -> bool:
    """Delete a document"""
    try:
        response = requests.delete(f"{API_BASE_URL}/documents/{document_id}")

        if response.status_code == 200:
            st.success("Document deleted successfully!")
            return True
        else:
            st.error(f"Error deleting document: {response.json().get('detail')}")
            return False

    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return False


# Main UI
st.title("🤖 Enterprise Knowledge Assistant")
st.markdown("*RAG-powered document analysis and question answering*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    page = st.radio(
        "Select Page",
        ["📤 Upload Documents", "❓ Ask Questions", "📚 Manage Documents"],
    )

    st.markdown("---")
    st.markdown("### API Status")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Unavailable")
    except:
        st.error("❌ API Unavailable")


# Page: Upload Documents
if page == "📤 Upload Documents":
    st.header("Upload PDF Documents")

    st.markdown("""
    Upload PDF documents to the knowledge base. The system will:
    1. Extract text from the PDF
    2. Split content into chunks
    3. Generate embeddings
    4. Store in vector database
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Select a PDF document to upload",
        )

    with col2:
        if st.button("📤 Upload", key="upload_btn", use_container_width=True):
            if uploaded_file is not None:
                with st.spinner("Uploading and processing..."):
                    upload_pdf(uploaded_file)
            else:
                st.warning("Please select a file first")

    st.markdown("---")
    st.subheader("Recent Uploads")

    documents = list_documents()
    if documents:
        for doc in documents[:5]:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.text(doc["original_filename"])
            with col2:
                status_emoji = "✅" if doc["status"] == "completed" else "⏳"
                st.text(f"{status_emoji} {doc['status']}")
            with col3:
                st.text(f"{doc['file_size'] / 1024 / 1024:.1f} MB")
    else:
        st.info("No documents uploaded yet")


# Page: Ask Questions
elif page == "❓ Ask Questions":
    st.header("Ask Questions")

    st.markdown("""
    Ask questions about the uploaded documents. The system will:
    1. Search for relevant document chunks
    2. Use GPT-4 to generate answers based on the context
    3. Show source references
    """)

    # Question input
    question = st.text_area(
        "Enter your question:",
        placeholder="What is this document about?",
        height=100,
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        top_k = st.slider(
            "Number of sources to consider:", min_value=1, max_value=20, value=5
        )

    with col2:
        if st.button("🔍 Search", key="ask_btn", use_container_width=True):
            if question.strip():
                with st.spinner("Searching and generating answer..."):
                    start_time = time.time()
                    result = ask_question(question, top_k)
                    elapsed_time = time.time() - start_time

                    if result:
                        st.markdown("### Answer")
                        st.write(result["answer"])

                        if result["sources"]:
                            st.markdown("### 📚 Sources Used")
                            for i, source in enumerate(result["sources"], 1):
                                with st.expander(
                                    f"Source {i} (Similarity: {source['similarity_score']:.2%})"
                                ):
                                    st.write(source["text_preview"])
                                    st.caption(
                                        f"Document ID: {source['document_id']} | Chunk ID: {source['chunk_id']}"
                                    )

                        st.markdown("---")
                        st.caption(
                            f"⏱️ Query time: {result['query_time_ms']:.0f}ms"
                        )
            else:
                st.warning("Please enter a question")


# Page: Manage Documents
elif page == "📚 Manage Documents":
    st.header("Manage Documents")

    st.markdown("View and manage uploaded documents")

    documents = list_documents()

    if documents:
        # Display documents in a table-like format
        for doc in documents:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])

            with col1:
                st.write(f"📄 {doc['original_filename']}")

            with col2:
                status_emoji = (
                    "✅" if doc["status"] == "completed"
                    else "⏳" if doc["status"] == "processing"
                    else "❌"
                )
                st.write(f"{status_emoji} {doc['status']}")

            with col3:
                st.write(f"{doc['file_size'] / 1024 / 1024:.1f} MB")

            with col4:
                st.write(doc["upload_date"].split("T")[0])

            with col5:
                if st.button("🗑️", key=f"delete_{doc['id']}", help="Delete document"):
                    if delete_document(doc["id"]):
                        st.rerun()

            if doc.get("error_message"):
                st.error(f"Error: {doc['error_message']}")

            st.markdown("---")

    else:
        st.info("No documents available")


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8rem;'>
    Enterprise Knowledge Assistant v1.0.0 | Built with FastAPI + LangChain + OpenAI
    </div>
    """,
    unsafe_allow_html=True,
)
