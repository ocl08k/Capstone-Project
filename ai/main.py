import asyncio
import re
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_community.document_loaders.json_loader import JSONLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from config import Config
from phoneme_correction import sentence_test
from sentence_analyse import test_classifier

args = Config()


def text_load(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        load = f.read()
        return load


class Vector_persistence:
    def __init__(self, collection_name):
        self.api = text_load(args.openai_api)
        self.persist_directory = args.chroma_directory
        self.embedding = OpenAIEmbeddings(
            openai_api_key=self.api,
            model=args.openai_embedding
        )
        self.chat = ChatOpenAI(
            openai_api_key=self.api,
            model=args.openai_chat
        )
        self.vector = Chroma(collection_name=collection_name, persist_directory=self.persist_directory,
                             embedding_function=self.embedding)

    def vector_save(self, file_path):
        json_loader = JSONLoader(file_path=file_path,
                                 jq_schema=args.json_jq_schema)
        json_document = json_loader.load()
        self.vector.add_documents(json_document)
        print(f"The file {file_path} is successfully saved as a vector.")

    async def llm_report(self, error_word_list, error_words_list, attitude, subject_name, sentence_label_list,
                         prompt_report=None):
        prompt_report = text_load(prompt_report)
        prompt_template = PromptTemplate(
            template=prompt_report,
            input_variables=["page_contents", "query", "attitude", "subject_name", "sentence_label_list"]
        )
        formatted_prompt = prompt_template.format(page_contents=error_word_list, query=error_words_list,
                                                  attitude=attitude, subject_name=subject_name,
                                                  sentence_label_list=sentence_label_list)
        response = self.chat.invoke(formatted_prompt)
        return response.content

    async def llm_dialogue(self, query, history, prompt_dialogue, k=None):
        prompt_dialogue = text_load(prompt_dialogue)
        similar_documents = self.vector.similarity_search(query, k=k or 1)
        page_contents = [doc.page_content for doc in similar_documents]
        prompt_template = PromptTemplate(
            template=prompt_dialogue,
            input_variables=["page_contents", "history", "query"]
        )
        formatted_prompt = prompt_template.format(page_contents=page_contents, history=history, query=query)
        print(formatted_prompt)
        response = self.chat.invoke(formatted_prompt)
        return response.content


async def answer_streaming(character, batch=3):
    if "animal" in character:
        subject_name = "bunny"
        robot = " Hi! I'm Dr. Paws from Funwattle, and I love helping all kinds of animals stay healthy! What's your favorite animal that you'd like to learn about caring for?"
        prompt_dialogue = args.prompt_animal
    elif "dolphin" in character:
        subject_name = "baby_dolphin"
        robot = "Hi there! I'm Dolphy-, your friendly dolphin buddy by FunWattle. I love to explore the sea and chat about all kinds of amazing sea creatures! Can you tell me about some of your favorite sea animals?"
        prompt_dialogue = args.prompt_dolphon
    elif "garden" in character:
        subject_name = "floret"
        robot =  "Hi! I'm Blossom the Garden Sprite! I love watching flowers grow in our magical garden! What's your favorite flower that you've seen before?"
        prompt_dialogue = args.prompt_garden
    elif "music" in character:
        subject_name = "minor_note"
        robot = "Hi! I'm Melody, the Musical Magician! I love creating magical music! What's your favorite musical instrument?"
        prompt_dialogue = args.prompt_music
    else:
        subject_name = "teddy bear"
        robot = "Hi! I'm Teddy, your cuddly bear friend! I love hearing about your day. What did you do today?"
        prompt_dialogue = args.prompt_teddybear
    vector = Vector_persistence(collection_name=str(character))
    error_phonemes_list = []
    reference_text_list = []
    history_list = []
    attitude = []
    score = {0: "high", 1: "medium", 2: "low"}
    yield robot, "", True
    for index in range(batch):
        for count in range(3):
            print(f"The {index + 1}/{count + 1} time...")
            error_sentence, reference_text = await sentence_test()
            answer = await vector.llm_dialogue(reference_text, history_list, prompt_dialogue=prompt_dialogue)
            answer = re.sub(r'[""]', '', answer)

            if len(reference_text.split()) > 1:
                attitude.append(score[count])
                error_phonemes_list.extend(error_sentence)
                reference_text_list.append(reference_text)
                history_list.append({
                    "multiple dialogue turns": index + 1,
                    "user": reference_text,
                    "reply": answer
                })
                yield answer, reference_text, True
                break
            else:
                yield answer, reference_text, True
            if count == 2:
                attitude.append(score[count])
    sentence_label_list = test_classifier(reference_text_list)
    report = await vector.llm_report(error_phonemes_list, reference_text_list, attitude, subject_name,
                                     sentence_label_list,
                                     prompt_report=args.prompt_report)
    yield report, error_phonemes_list, False


async def main():
    async for output in answer_streaming(character="dolphin", batch=3):
        answer, reference_text, is_intermediate = output
        print(f"Answer: {answer}")
        print(f"Reference Text: {reference_text}")
        print(f"Is Intermediate: {is_intermediate}")


if __name__ == '__main__':
    asyncio.run(main())