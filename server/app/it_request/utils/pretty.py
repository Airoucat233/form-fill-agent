from langchain_core.messages import convert_to_messages


def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # 跳过父图更新以避免冗余输出
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"来自子图 {graph_id} 的更新：")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"来自节点 {node_name} 的更新："
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")
