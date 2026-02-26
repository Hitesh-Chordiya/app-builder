from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class File(BaseModel):
    path: str = Field(description="The path of the file to be created")
    purpose: str = Field(description="The purpose of the file to be created e.g 'Main application logic', 'Data processing module', 'etc.'")

class Plan(BaseModel):
    name: str = Field(description="The name of the app to be built")
    description: str = Field(description="The description of the app to be built")
    techStack: str = Field(description="The tech stack of the app to be built e.g 'Python', 'Java', 'etc.'")
    features: list[str] = Field(description="The list of features of the app to be built e.g 'user authentication', 'data visualization', etc.'")
    files: list[File] = Field(description="The list of files to be created, each with a 'path' and 'purpose'")

class ImplementationTask(BaseModel):
    filePath: str = Field(description="The path of the file to be updated")
    taskDescription: str = Field(description="The description of the task to be performed on the file, e.g 'add user authentication', 'implement data processing logic', etc.'")

class TaskPlan(BaseModel):
    implementationTasks: list[ImplementationTask] = Field(description="The list of tasks to be performed on the implementation")
    model_config = ConfigDict(extra="allow")

class CoderState(BaseModel):
    task_plan: TaskPlan = Field(description="The plan for the task to be implemented")
    current_step_idx: int = Field(0, description="The index of the current step in the implementation steps")
    current_file_content: Optional[str] = Field(None, description="The content of the file currently being edited or created")