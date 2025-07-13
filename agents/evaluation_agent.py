def evaluate_node(state):
    scored = sorted(state["results"].items(), key=lambda x: x[1]["sharpe"], reverse=True)
    top3 = [name for name, _ in scored[:3]]
    return {"stock": state["stock"], "top_3": top3, "scored": scored}
