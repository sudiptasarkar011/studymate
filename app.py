from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA
import gradio as gr

# Load the PDF
loader = PDFPlumberLoader("UNIT_1(SE).pdf")
docs = loader.load()

# Split into chunks
text_splitter = SemanticChunker(HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
documents = text_splitter.split_documents(docs)

# Instantiate the embedding model
embedder = HuggingFaceEmbeddings()

# Create the vector store and fill it with embeddings
vector = FAISS.from_documents(documents, embedder)
retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Define llm
llm = Ollama(model="mistral")

# Define the prompt
prompt = """
1. Use the following pieces of context to answer the question at the end.
2. If you don't know the answer, just say that "I don't know" but don't make up an answer on your own.\n
3. Keep the answer crisp and limited to 3,4 sentences.

Context: {context}

Question: {question}

Helpful Answer:"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt) 

llm_chain = LLMChain(
                  llm=llm, 
                  prompt=QA_CHAIN_PROMPT, 
                  callbacks=None, 
                  verbose=True)

document_prompt = PromptTemplate(
    input_variables=["page_content", "source"],
    template="Context:\ncontent:{page_content}\nsource:{source}",
)

combine_documents_chain = StuffDocumentsChain(
                  llm_chain=llm_chain,
                  document_variable_name="context",
                  document_prompt=document_prompt,
                  callbacks=None)
              
qa = RetrievalQA(
                  combine_documents_chain=combine_documents_chain,
                  verbose=True,
                  retriever=retriever,
                  return_source_documents=True)

def respond(question,history):
    return qa(question)["result"]

gr.Interface(
    fn=respond,
    inputs=gr.Textbox(placeholder="Ask me question related to Software Engineering", container=False, scale=7),
    outputs=gr.Textbox(),
    title="SDE's Chatbot",
    examples=["Why we use SDLC", "What are disadvantages of Build and Fix Model"],
    cache_examples=True,
).launch(share=True)
