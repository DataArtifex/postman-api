import os
from dotenv import load_dotenv
from dartfx.postmanapi import postman_collection_pd as pc

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("POSTMAN_API_KEY")
model = ChatOpenAI(temperature=0)

def test_collection_instructions():
    # prompt
    parser = PydanticOutputParser(pydantic_object=pc.Collection)
    #print(parser.get_format_instructions())
    prompt = PromptTemplate(
        template="Generate a Postman Collection illustrating the use case below.\n{format_instructions}\nUse case:{use_case}",
        input_variables=["use_case"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    collection = chain.invoke({"use_case": "getting city weather"})
    
    outfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'output', "langchain_collection.json")
    
    collection.save(outfile)
    
    assert collection.info
