from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.globals import set_debug, set_verbose
from langchain_groq import ChatGroq
from langgraph.constants import END
from langgraph.graph import StateGraph

from agent.prompt import planner_prompt, architect_prompt, coder_system_prompt
from agent.states import Plan, TaskPlan, CoderState
from agent.tools import *

load_dotenv()
set_debug(True)
set_verbose(True)

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)


def planner_agent(state: dict) -> Plan:
    user_prompt: str = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    if resp is None:
        raise ValueError("Planner did not return a response")
    state["plan"] = resp


def architect_agent(state: dict) -> Plan:
    prompt: Plan = state["plan"]
    resp = llm.with_structured_output(TaskPlan).invoke(architect_prompt(prompt))
    if resp is None:
        raise ValueError("Architect did not return a response")
    state["architect"] = resp


def coder_agent(state: dict) -> Plan:
    coder_state: CoderState = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(task_plan=state["architect"], current_step_idx=0)
    steps = coder_state.task_plan.implementationTasks
    if coder_state.current_step_idx >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = steps[coder_state.current_step_idx]
    existing_content = read_file.run(current_task.filePath)

    system_prompt = coder_system_prompt()
    user_prompt = (
        f"Task: {current_task.taskDescription}\n"
        f"File: {current_task.filePath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )

    coder_tools = [read_file, write_file, list_files, get_current_directory]
    react_agent = create_agent(llm, coder_tools)

    react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                      {"role": "user", "content": user_prompt}]})

    coder_state.current_step_idx += 1
    return {"coder_state": coder_state}


graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)
graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_conditional_edges(
    "coder",
    lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"})
graph.set_entry_point("planner")
agent = graph.compile()

user_prompt = "Create a to-do list application using html, css, and javascript"
state = {
    "user_prompt": user_prompt
}
if __name__ == '__main__':
    result = agent.invoke(state)
    print(result)
