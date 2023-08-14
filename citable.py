from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from dotenv import load_dotenv
load_dotenv()


llm = OpenAI(temperature=0)

# Chain A
template = """You are a bot that identifies a segment within an essay or written work that requires citation.

New Essay: {essay}
Response:"""
prompt = PromptTemplate.from_template(template)
segment_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    output_key="segment",
)

# Chain B
template = """You are a bot that evaluate whether a given segment from an essay meets the following criteria for citation:
Paraphrased information: Restating someone else's ideas in your own words,
Summarized information: Condensing the main points of someone else's work, or
Sources: Books, articles, websites, etc., that you refer to or draw information from.

Segments with the following attributes are NOT elligible for citation:
Statistics and data: Any numerical information not considered common knowledge.
Images, diagrams, and illustrations: Any visual elements not created by you.
Direct quotes: Any exact wording from a source.

Essay Segment: {segment}
Essay: {essay}

Provide whether the segment is valid and which qualifying/disqualifying criteria it matches.
"""

prompt = PromptTemplate(template=template, input_variables=[
                        'segment', 'essay'],)
evaluator_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    output_key="validation",
)

# Chain C

response_schemas = [
    ResponseSchema(
        name="segment", description="segment from text that requires citation"),
    ResponseSchema(name="is_valid", description="", type="boolean"),
    ResponseSchema(name="criteria",
                   description="criteria which validated the segment")
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

template = """
Format the following text sample according to the format instructions below:
{segment}, {validation}
{format_instructions}"""
prompt = PromptTemplate(template=template, input_variables=["segment", "validation"], partial_variables={
                        "format_instructions": output_parser.get_format_instructions()})
output_chain = LLMChain(llm=llm, prompt=prompt,
                        output_key="output", output_parser=output_parser)

citable_sequential_chain = SequentialChain(
    chains=[segment_chain, evaluator_chain, output_chain], input_variables=["essay"], output_variables=["output"])


def chunk_merge(texts_list: list, chunk_size: int):
    newdoc = []
    doclist = []
    while texts_list:
        newdoc.extend(texts_list.pop())
        diff = len(newdoc) - chunk_size
        if diff > 0:
            doclist.append(' '.join(word for word in newdoc[diff:]))
            remainder = newdoc[:diff]
            newdoc = []
            newdoc.extend(remainder)
    if len(newdoc) > 0:
        doclist.append(' '.join(word for word in newdoc))
    return doclist


def split_texts(text, paragraph_break="\n\n"):
    space_seperated_paragraphs = text.split(paragraph_break)
    for idx, pg in enumerate(space_seperated_paragraphs):
        space_seperated_paragraphs[idx] = pg.split()
    return space_seperated_paragraphs


def chunk_texts(text: str, chunk_size: int, paragraph_break: str = "\n\n"):
    return chunk_merge(split_texts(text, paragraph_break), chunk_size)


# text ="""The Timeless Beauty of Mozart: A Musical Genius Beyond Compare

# Mozart, the mere mention of his name evokes a sense of wonder and admiration for his unparalleled musical brilliance. Wolfgang Amadeus Mozart, born in 1756, remains an iconic figure in the world of classical music, his compositions immortalizing his genius across centuries. His music transcends time, captivating audiences with its sheer beauty, intricate craftsmanship, and emotional depth. The beauty of Mozart's work lies not only in its melodic grace and technical mastery but also in its ability to evoke powerful emotions and connect humanity through the language of music.

# Mozart's music is characterized by its effortless elegance and lyrical grace. His compositions exhibit a harmonious blend of melody and structure, creating an auditory experience that feels both natural and meticulously crafted. Take, for instance, his Symphony No. 40 in G minor. The symphony opens with a dramatic and haunting melody, immediately drawing the listener into its emotional depths. As the music unfolds, Mozart weaves intricate melodies and harmonic progressions, effortlessly transitioning between different moods and themes. This symphony showcases Mozart's ability to balance complexity with accessibility, allowing both the seasoned music enthusiast and the casual listener to appreciate its beauty.

# One of the defining aspects of Mozart's music is its emotional resonance. He had an uncanny ability to express a wide range of emotions through his compositions, from the exuberant joy of his "Eine kleine Nachtmusik" to the profound introspection of his Requiem Mass in D minor. The exquisite beauty of his Adagio movements, such as those in his piano concertos, is particularly notable. These movements often possess a delicate and introspective quality, inviting listeners to reflect and connect with their own emotions. Mozart's ability to capture the human experience through musical notes is a testament to his deep understanding of the human psyche and his gift for translating emotions into sounds that resonate across cultures and eras.

# Technical virtuosity was another hallmark of Mozart's music. His compositions challenge performers with their intricate ornamentation, rapid passages, and demanding dynamics. Yet, this technical prowess is always in service of the music's expressive intent. Mozart's piano sonatas, for example, reveal his mastery of the keyboard as well as his innovative approach to form and structure. The "Rondo alla Turca" from his Piano Sonata No. 11 is a prime example, where dazzling runs and catchy melodies create a delightful contrast, captivating both the listener's ears and heart.

# Mozart's operatic works further underscore his ability to create beauty through collaboration. His operas are not just showcases for his musical genius but also platforms for exploring the depths of human relationships, desires, and conflicts. Operas like "The Marriage of Figaro" and "Don Giovanni" are masterpieces of storytelling and character development, enhanced by Mozart's richly expressive music. His arias have the power to move listeners to tears or laughter, revealing the intricacies of the characters' inner worlds. In these operatic works, the beauty of Mozart's music intertwines with the beauty of the human voice and the theatrical performances, resulting in a multi-sensory experience that resonates profoundly.

# Mozart's ability to craft music that remains relevant and inspiring through the ages is a testament to his universality. His compositions appeal to people of diverse backgrounds and tastes, transcending cultural and temporal boundaries. Whether it's a grand symphony performed by a full orchestra or a delicate piano piece played in an intimate setting, the essence of Mozart's beauty endures. This timeless quality is beautifully encapsulated in his Piano Concerto No. 21, popularly known as the "Elvira Madigan" concerto. Its second movement, marked "Andante," is a serene and melancholic piece that has found its way into countless films, commercials, and cultural references. The fact that this movement, composed more than two centuries ago, can still evoke powerful emotions in today's audience attests to Mozart's enduring legacy.

# In conclusion, the beauty of Mozart's music is a multi-faceted gem that continues to shine brightly in the annals of classical music history. His compositions embody elegance, emotional depth, technical brilliance, and universal appeal. Mozart's music transcends time, cultural boundaries, and individual preferences, speaking directly to the human soul. Through his symphonies, operas, and instrumental works, he has left an indelible mark on the world of music, enriching lives and reminding us of the profound beauty that can be created through artistic expression. As we listen to the melodies and harmonies that flowed from his pen, we are reminded that true beauty is eternal, and Mozart's legacy remains an everlasting testament to that truth."""

# print(chunk_texts(text, 300))
