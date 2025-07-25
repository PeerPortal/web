"""
知识库管理模块
实现文档处理、向量化存储和RAG检索功能
"""
import os
import shutil
from typing import List, Optional
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import tool
from app.core.config import settings

VECTOR_STORE_PATH = "./vector_store"
KNOWLEDGE_BASE_PATH = "./knowledge_base"

class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            chunk_size=100  # 减小批处理大小，避免超过token限制
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # 减小chunk大小
            chunk_overlap=50  # 减小重叠
        )
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """保存上传的文件到知识库目录"""
        os.makedirs(KNOWLEDGE_BASE_PATH, exist_ok=True)
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path
    
    def load_and_embed_knowledge_base(self) -> Optional[Chroma]:
        """加载、分割、嵌入并存储知识库文档"""
        print("🔍 扫描知识库文件...")
        
        # 1. 检查知识库目录
        if not os.path.exists(KNOWLEDGE_BASE_PATH) or not os.listdir(KNOWLEDGE_BASE_PATH):
            print("📂 知识库为空，跳过嵌入过程。")
            return None
        
        # 2. 加载文档
        documents = []
        for file_name in os.listdir(KNOWLEDGE_BASE_PATH):
            file_path = os.path.join(KNOWLEDGE_BASE_PATH, file_name)
            if file_name.lower().endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
            elif file_name.lower().endswith(('.txt', '.md')):
                # 支持文本文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    from langchain.schema import Document
                    doc = Document(page_content=content, metadata={'source': file_path})
                    documents.append(doc)
        
        if not documents:
            print("📝 没有找到支持的文档格式，跳过嵌入过程。")
            return None
        
        print(f"📚 找到 {len(documents)} 个文档页面")
        
        # 3. 分割文档
        splits = self.text_splitter.split_documents(documents)
        print(f"✂️ 文档分割完成，共 {len(splits)} 个文档块")
        
        # 如果文档块太多，限制数量避免token超限
        if len(splits) > 500:
            print(f"⚠️ 文档块数量({len(splits)})过多，只处理前500个避免token超限")
            splits = splits[:500]
        
        # 4. 创建并持久化向量数据库
        print("🧠 正在创建向量数据库...")
        
        # 如果向量库已存在，先删除
        if os.path.exists(VECTOR_STORE_PATH):
            shutil.rmtree(VECTOR_STORE_PATH)
        
        try:
            # 批量处理，每次处理50个文档块
            batch_size = 50
            vectorstore = None
            
            for i in range(0, len(splits), batch_size):
                batch = splits[i:i+batch_size]
                print(f"  📦 处理第 {i//batch_size + 1} 批，共 {len(batch)} 个文档块")
                
                if vectorstore is None:
                    # 第一批创建向量库
                    vectorstore = Chroma.from_documents(
                        documents=batch,
                        embedding=self.embeddings,
                        persist_directory=VECTOR_STORE_PATH,
                        collection_name="knowledge_base"
                    )
                else:
                    # 后续批次添加到现有向量库
                    vectorstore.add_documents(batch)
            
        except Exception as e:
            print(f"⚠️ ChromaDB创建失败: {e}")
            # 降级处理：只使用留学申请成功案例.txt
            txt_files = [doc for doc in documents if doc.metadata.get('source', '').endswith('.txt')]
            if txt_files:
                print("🔄 降级处理：只使用TXT文件重建知识库")
                txt_splits = self.text_splitter.split_documents(txt_files)
                try:
                    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
                    vectorstore = Chroma.from_documents(
                        documents=txt_splits,
                        embedding=self.embeddings,
                        persist_directory=VECTOR_STORE_PATH,
                        collection_name="knowledge_base"
                    )
                except Exception as e2:
                    print(f"❌ 降级处理也失败: {e2}")
                    return None
            else:
                return None
        
        print("✅ 向量数据库创建完成！")
        return vectorstore
    
    def get_retriever(self, k: int = 3):
        """获取现有的向量数据库检索器"""
        if not os.path.exists(VECTOR_STORE_PATH):
            # 如果向量库不存在，尝试创建
            vectorstore = self.load_and_embed_knowledge_base()
            if vectorstore is None:
                return None
        else:
            try:
                vectorstore = Chroma(
                    persist_directory=VECTOR_STORE_PATH,
                    embedding_function=self.embeddings,
                    collection_name="knowledge_base"
                )
            except Exception as e:
                print(f"⚠️ 加载向量数据库失败: {e}")
                # 如果加载失败，尝试重新创建
                vectorstore = self.load_and_embed_knowledge_base()
                if vectorstore is None:
                    return None
        
        return vectorstore.as_retriever(search_kwargs={"k": k})
    
    def get_knowledge_base_stats(self) -> dict:
        """获取知识库统计信息"""
        stats = {
            "files_count": 0,
            "vector_store_exists": os.path.exists(VECTOR_STORE_PATH),
            "files": []
        }
        
        if os.path.exists(KNOWLEDGE_BASE_PATH):
            files = os.listdir(KNOWLEDGE_BASE_PATH)
            stats["files_count"] = len(files)
            stats["files"] = files
        
        return stats

# 创建全局实例
knowledge_manager = KnowledgeBaseManager()

@tool
def knowledge_base_retriever(query: str) -> List[str]:
    """
    从私有知识库中检索相关信息。
    当需要回答关于留学申请策略、特定学校的内部信息、文书写作技巧或过往成功案例时使用此工具。
    这个工具能从平台的私有知识库中检索最相关的信息。
    """
    try:
        retriever = knowledge_manager.get_retriever()
        if retriever is None:
            return ["📚 知识库为空，请先上传相关文档。您可以上传PDF格式的留学申请案例、学校介绍、文书指导等文档来丰富知识库。"]
        
        docs = retriever.invoke(query)
        if not docs:
            return ["📝 在知识库中没有找到相关信息，建议使用网络搜索获取最新信息。"]
        
        results = []
        for i, doc in enumerate(docs, 1):
            # 获取文档来源
            source = doc.metadata.get('source', '未知来源')
            source_name = os.path.basename(source) if source != '未知来源' else source
            
            results.append(f"📖 来源 {i}: {source_name}\n内容: {doc.page_content}\n")
        
        return results
        
    except Exception as e:
        return [f"❌ 知识库检索出错: {str(e)}"]

@tool  
def get_knowledge_base_stats() -> str:
    """
    获取知识库的统计信息，包括文档数量和状态。
    当用户询问知识库状态或想了解有哪些文档时使用此工具。
    """
    try:
        stats = knowledge_manager.get_knowledge_base_stats()
        
        result = f"""📊 知识库状态报告:
        
📁 文档数量: {stats['files_count']} 个文件
🧠 向量库状态: {'已建立' if stats['vector_store_exists'] else '未建立'}

📚 已上传的文档:"""

        if stats['files']:
            for file in stats['files']:
                result += f"\n  • {file}"
        else:
            result += "\n  暂无文档"
            
        if not stats['vector_store_exists'] and stats['files_count'] > 0:
            result += "\n\n💡 提示: 检测到有文档但向量库不存在，建议重新构建知识库。"
            
        return result
        
    except Exception as e:
        return f"❌ 获取知识库状态失败: {str(e)}"
