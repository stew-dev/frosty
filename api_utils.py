from starlette.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3001",
    "localhost:3001",
    "192.168.5.82:3001",
    "http://192.168.5.82:3001"
]


def disable_security(api):
    api.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
