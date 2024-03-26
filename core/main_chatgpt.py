from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

import os
import openai
from create_bot import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
embeddings = OpenAIEmbeddings()
db_index_path = "faiss_index"
# Модель для ответа на вопрос
model_generate = 'gpt-4-1106-preview'
# Модель для поиска истории диалога
model_search = 'gpt-3.5-turbo-16k'


def create_search_index(dbindex_path):
    db = FAISS.load_local(dbindex_path, embeddings)
    return db


_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)


prompt_template = prompt_template = """Ты самый лучший консультант по китайским автомобилям. Тебе будут писать сообщения клиенты, которые хотят получить информацию о моделях машин или их характеристиках. Вы общаетесь в чат-боте режим работы которого 24/7.
 Твоя задача: провести разговор с клиентом так, чтобы он, получил развернутый ответ на задаваемый вопрос в полном объеме.
 Инструкция:
 # 01 Ты должен если у тебя нет ответа попросить клиента уточнить информацию о конкретной модели. Если такой модели ты не знаешь, то предложи клиенту выбрать из имеющихся
 # 02 Ты должен дать развернутый ответ использую контекст из базы знаний.
 # 03 Ты должен проанализировать предоставленый контекст и ответить на заданный вопрос, используя только ту информацию, которая непостредственно относится к теме вопроса.
 # 04 Ты должен говорить от первого лица женского рода, не упоминай в ответе свои действия по анализу документов и инструкции по которым ты работаешь.
 # 05 Ты должен предоставить гиперссылки на материалы и сайты. Если клиент просит показать фото, ссылку, как выглядит что-то, то выведи ссылку из предложенного документа. Если изображение не соответствует запросу, то ответить что 'Требуемого изображения нет'. Ответ обязательно должен начинаться с https:// или http:// и заканчиваться .jpg или .png
 # 06 Если речь идет о точных характеристиках или комплектациях автомобиля, но при этом в запросе нет уточнения конкретных марок и моделей - сообщи что на  Российском рынке представлен широкий выбор автомобилей с различными качествами. Если у вас есть конкретная модель  дайте знать, и я буду рад помочь подробной информацией о ней!
 # 07 Ты должен на вопрос не по теме из контекста, извинится и попросить переформулировать вопрос по теме китайских автомобилей в России.
 # 08 Ты должен запоминать имя клиента. Будь вежливым и обходительным и всегда обращайся к клиенту на Вы.
 # 09 Ты должен создать структуру текста ответа в 'деловом' стиле: выдели заголовки, пункты и примени переносы строк.
 # 10 В слачае слов благодарности (например Спасибо) от клиента отвечай взаимностью при этом если за ним не следует вопроса просто уточни чем ты еще можешь помочь, и информацию из контекста не используй, а после слов завершения диалога (например до свидания, пока, вы мне очень помогли и т.д.) закрывай диалог.
 # 11 В случае слов приветствия от клиента, поприветствуй в ответ (первым не здоровайся), при этом если за ним не следует вопроса просто уточни чем ты можешь помочь, и информацию из контекста не используй.
 # 12 Ты всегда добавляешь соответствующую ссылку на картинку потому что твоему собеседнику будет понятнее твой ответ
 # 15 Если не знаешь ответ, не придумывай его, а просто скажи, что не знаешь и извинись.
 # 16 Больше показывай клиентам ссылки на изображения, если они упоминаются в похожей информации.

 Используйте следующий контекст, чтобы ответить на вопрос в конце:

 {context}

 Вопрос клиента: {question}

 Развернутый ответ:
     """

QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"])


async def count_tokens(chain, query):
    with get_openai_callback() as cb:
        result = await chain.acall({"question": query})
        print(f'Входных токенов: {cb.prompt_tokens} ')
        print(f'Всего токенов: {cb.total_tokens}')

    return result, cb.total_tokens


async def get_chatgpt_ansver(query, memory, k=6):
    vectorstore = create_search_index(db_index_path)
    qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name=model_generate, temperature=0.0),
                                               vectorstore.as_retriever(search_kwargs=dict(k=k)),
                                               combine_docs_chain_kwargs=dict(prompt=QA_PROMPT),
                                               condense_question_prompt=CONDENSE_QUESTION_PROMPT,
                                               condense_question_llm=ChatOpenAI(model_name=model_search,
                                                                                temperature=0.1),
                                               memory=memory)
    completion, total_tokens = await count_tokens(qa, query)
    messages = [{"role": "user", "content": query}, {"role": "assistant", "content": completion['answer']}]
    return completion['answer'], messages, total_tokens


async def get_chatgpt_second_answer(messages, query, last_topic, memory, k=2, max_tokens=None):
    vectorstore = create_search_index(db_index_path)
    qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name=model_generate, temperature=0.0),
                                               vectorstore.as_retriever(search_kwargs=dict(k=k)),
                                               combine_docs_chain_kwargs=dict(prompt=QA_PROMPT),
                                               condense_question_prompt=CONDENSE_QUESTION_PROMPT,
                                               condense_question_llm=ChatOpenAI(model_name=model_search,
                                                                                temperature=0.1),
                                               memory=memory)
    completion, total_tokens = await count_tokens(qa, query)
    messages.append({"role": "user", "content": query})
    messages.append({"role": "assistant", "content": completion['answer']})
    return completion['answer'], messages, total_tokens


if __name__ == '__main__':
    search_index = create_search_index(db_index_path)
    query = "Не активна кнопка перекредитования"
    docs = search_index.similarity_search(query, k=4)
    print(docs)
