def build_history(history):

    messages = []

    for msg in history[-6:]:

        messages.append(
            f"""
{msg['role'].upper()}:

{msg['content']}
"""
        )

    return "\n".join(messages)
