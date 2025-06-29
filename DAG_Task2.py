from airflow.sdk import dag, task, Asset

COLLECTION_NAME = "Books"  
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"


@dag(
    schedule=[Asset("my_book_vector_data")]
) #new!
def query_data():

    @task
    def search_vector_db_for_a_book(query_str: str):
        from airflow.providers.weaviate.hooks.weaviate import WeaviateHook
        from fastembed import TextEmbedding

        hook = WeaviateHook("my_weaviate_conn")
        client = hook.get_conn()

        embedding_model = TextEmbedding(EMBEDDING_MODEL_NAME)  
        collection = client.collections.get(COLLECTION_NAME)
        
        query_emb = list(embedding_model.embed([query_str]))[0]
        
        results = collection.query.near_vector(
            near_vector=query_emb,
            limit=1,
        )
        for result in results.objects:
            print(f"You should read: {result.properties['title']} by {result.properties['author']}")
            print("Description:")
            print(result.properties["description"])

    search_vector_db_for_a_book(query_str="A philosophical book")


query_data()
