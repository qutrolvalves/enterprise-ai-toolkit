from ..config import OPENAI_API_KEY
import openai
openai.api_key = OPENAI_API_KEY

def quote_agent_process(message):
    response = openai.ChatCompletion.create(
        model='gpt-5-mini',
        messages=[{'role':'user','content': f'客户消息：{message}，生成详细报价'}]
    )
    return response['choices'][0]['message']['content']
