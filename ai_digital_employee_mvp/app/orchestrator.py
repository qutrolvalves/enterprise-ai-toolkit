from .agents.sales_agent import sales_agent_process
from .agents.tech_agent import tech_agent_process
from .agents.quote_agent import quote_agent_process
from .agents.followup_agent import followup_agent_process

def orchestrate_request(message):
    sales_result = sales_agent_process(message)
    tech_result = tech_agent_process(message)
    quote_result = quote_agent_process(message)
    followup_result = followup_agent_process(message)
    return {
        'sales': sales_result,
        'tech': tech_result,
        'quote': quote_result,
        'followup': followup_result
    }
