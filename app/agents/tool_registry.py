from agno.tools import Toolkit

TOOL_REGISTRY: dict[str, dict] = {}

class RegisteredToolkit(Toolkit):
    tool_key: str | None = None

    def __init_subclass__(cls, key: str | None = None, name: str | None = None,
                          desc: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if key is None:
            return
        if key in TOOL_REGISTRY and TOOL_REGISTRY[key]["cls"].__qualname__ != cls.__qualname__:
            raise RuntimeError(f"Duplicate tool key '{key}'")
        cls.tool_key = key
        TOOL_REGISTRY[key] = {
            "cls": cls,
            "name": name or key,
            "desc": desc or (cls.__doc__ or "").strip(),
        }