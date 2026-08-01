import yaml

class GiuliaAIPrompts:
    def __init__(self, name, description=None, tool_args=None):
        self.name = name
        self.description = description
        self.tool_args = tool_args or []

    def yaml_str(self):
        data = {
            "name": self.name,
            "description": self.description,
            "args": self.tool_args
        }
        return yaml.dump(data, allow_unicode=True)

    @classmethod
    def get_prompt_by_name(cls, prompts, name):
        for p in prompts:
            if p.name == name:
                return {
                    "name": p.name,
                    "description": p.description,
                    "args": p.tool_args
                }
        return None
