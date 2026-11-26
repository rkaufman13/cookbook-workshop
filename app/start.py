from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from config import get_settings
from validators import contains_url
from recipe_parsing import parse_recipe
from templatizer import generate_and_encode_template
from github_api_helpers import create_pr_off_main

settings = get_settings()
pattern = f"{settings.admin_email}"
github_api_key = settings.github_api_key


class EmailPayload(BaseModel):
    Date: str
    from_email: str = Field(..., alias="from")
    stripped_text: str = Field(..., alias="stripped-text")
    recipient: str = Field(..., pattern=pattern)


class IncomingEmail(BaseModel):
    payload: EmailPayload


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/test-message")
async def parse_message(message: IncomingEmail):
    message_body = message.payload.stripped_text
    recipe_urls = contains_url(message_body)
    if not len(recipe_urls):
            return {"message": "no url(s) found in message body"}
    for recipe_url in recipe_urls:
        recipe = parse_recipe(recipe_url)
        if recipe:
            return recipe
        return {"message": f"no recipe found at URL {recipe_url}"}


@app.post("/incoming-message")
async def parse_message(message: IncomingEmail):
    message_body = message.payload.stripped_text
    message_sender = message.payload.from_email.split(" ")[0].replace("\"","")
    recipe_url = contains_url(message_body)
    if not recipe_url:
        return {"message": "no url found"}
    recipe = parse_recipe(recipe_url)
    if not recipe:
        return {"message": f"no recipe found at URL {recipe_url}"}
    encoded_template, filename = generate_and_encode_template(recipe, message_sender)
    create_pr_off_main(encoded_template, filename)
    return {"message": f"recipe found at URL {recipe_url}, opening PR"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8013)
