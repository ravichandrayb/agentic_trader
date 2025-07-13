from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from strategies.strategy_registry import get_example_strategies

llm = ChatOpenAI(model="gpt-4", temperature=0.3)

def generate_strategies_node(state):
    stock = state["stock"]
    examples = get_example_strategies()

    # Build few-shot examples into the prompt
    example_messages = []
    for ex in examples:
        user_msg = f"Generate a strategy using {', '.join(ex['indicators'])}"
        assistant_msg = (
            f"Strategy Name: {ex['name']}\n"
            f"Description: {ex['description']}\n"
            f"Entry Rule: {ex['entry_rule']}\n"
            f"Exit Rule: {ex['exit_rule']}"
        )
        example_messages.extend([
            ("user", user_msg),
            ("assistant", assistant_msg)
        ])

    # Final user task
    example_messages.append((
        "user",
        f"Generate 5 technical trading strategies for the stock {stock} using pandas_ta indicators. "
        f"Return only strategy name, description, entry_rule, and exit_rule in JSON format."
    ))

    # Add system prompt
    messages = [("system", "You are an expert quant who uses pandas_ta for building trading strategies.")]
    messages.extend(example_messages)

    # Generate
    prompt = ChatPromptTemplate.from_messages(messages)
    response = llm(prompt.format_messages())[0].content

    return {"stock": stock, "strategies": response}
