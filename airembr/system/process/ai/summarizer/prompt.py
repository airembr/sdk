from typing import Optional

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.settings import ModelSettings
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai import Agent

from system.process.ai.summarizer.model.summary_output import SummaryOutput
from airembr.system.config.llm_config import llm_config



async def get_summary(text) -> Optional[SummaryOutput]:
    if llm_config.llm_token is None or llm_config.llm_model is None or llm_config.llm_provider is None:
        return None

    if llm_config.llm_provider == 'openrouter':
        provider = OpenRouterProvider(api_key=llm_config.llm_token)
    else:
        return None

    # Prompt
    model = OpenAIModel(
        llm_config.llm_model,
        settings=ModelSettings(temperature=.1),
        provider=provider
    )

    agent = Agent(
        model,
        system_prompt=(
            "Your objective is to: \n"
            " - summarize the following conversation into a several sentence (list of facts), capturing the most essential information "
            " - retrieve max 5 one-word topics mentioned in the conversation."
        ),
        output_type=SummaryOutput
    )

    prompt = f"""
    Your Task:
    
    "Provide a comprehensive summary of the given conversation in form of list of facts. 
    Use the previous summary as a reference of the last chat compression and as context for the conversation. 
    The summary should cover all key topics, participants, and main ideas from the original text in multiple concise, 
    one-sentence facts. 
    Avoid unnecessary information or repetition. 
    Include any new facts from the current conversation at the end of the summary."
    
    Summary Rules:
    
    - Complete Coverage: Include every significant fact, idea, decision, or action discussed. Do not omit anything important.
    - Participants: Mention all people involved, their roles, and contributions if relevant.
    - Key Details: Always include all numbers, dates, locations, references, or technical details mentioned.
    - Topic Clarity: Clearly distinguish between different topics or threads discussed.
    - Conclusions and Findings: If the conversation ends with conclusions, arrangements, decisions, numbers, or findings, mention them explicitly at the end. Summary must mention all facts, arrangements, etc coming form the conversation so it can continue after reading last sentence.
    - New Facts: Any new information not included in the previous summary must be appended at the end in one-sentence facts.
    - Conciseness: Present each fact as a single, clear sentence. Avoid repetition or filler.
    - Context Preservation: Maintain cause-effect or relational context between points where relevant.
    - Memory-Friendly: Organize the summary logically (bullet points or numbered list) to make it easy to review and memorize.
    
    --- Text to Summarize ---
    {text}
    """

    result = await agent.run(prompt)
    return result.output
