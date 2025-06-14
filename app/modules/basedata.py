from pydantic import BaseModel


class BaseData(BaseModel):
	appname: str
	location: str
	time: str
	images: list[str] = []
	transcription: list[str]


class ImageDescription(BaseModel):
	image: str
	description: str


transcription_ladder = [
	"0, 113 emergency,  you're speaking to a nurse Thomas, how may I help you?",
	"1, Please help us.",
	"1, My sister fell down from a ladder. She's unconscious.",
	"0, OK. Can you confirm your calling from Main Street 15?",
	"1, Yes, that's yes, we are in Main Street 15.",
	"0, OK. Can you tell me if the person is conscious and breathing?",
	"1, She's breathing.",
	"1, But Hilda, Hilda, can you hear me?",
	"1, Hilda, please open your eyes, Hilda.",
	"1, She's moaning and she's trying to open her eyes, but I can't get anything out of her.",
	"0, OK, OK. Check if she's breathing normally or or if there are any signs of difficulty.",
	"1, She's breathing.",
	"1, There is air passing.",
	"1, I don't think she has any difficulty breathing.",
	"0, OK.",
	"0, Check her head and and keep her head stable and avoid moving her.",
	"1, OK, my my brother can help with doing that, but I'm really concerned she has.",
	"1, She's broken her leg.",
	"1, Can you see this?",
	"1, And it's bleeding really bad.",
	"0, Yeah, I can see it.",
	"1, Seems to be an open fracture.",
	"0, You need  to apply pressure to the bleeding area with a clean cloth or bandage to stop the bleeding.",
	"1, OK.",
	"1, Just a minute. We'll do that.",
	"0, You should also elevate the injured leg to reduce bleeding if possible.",
	"1, OK, I have a clean cloth here and just apply it directly here where it's bleeding.",
	"1, And elevate the leg.",
	"1, Oh, this is painful for her.",
	"1, I'm sorry, Hilda.",
	"0, And.",
	"1, I think she's waking up a little bit now. Does this seem OK?",
	"1, OK.",
	"0, I think so. And sure the bleeding area is elevated as high as possible to help reduce blood loss.",
	"0, Don't give her anything to drink or eat.",
	"1, OK, we we won't do that.",
	"0, OK. Can you also try to keep her warm with a blanket or coat?",
	"1, Yes, we'll do that.",
	"0, Endure she's lying on her side to prevent choking if she vomits.",
	"1, OK.",
	"1, I don't know if I can move her right now.",
	"1, With this broken leg.",
	"0, OK.",
	"0, And then.",
	"1, Hilda.",
	"0, OK.",
	"1, Yeah, she's. She's waking up a little bit now.",
	"0, OK.",
	"0, So she's breathing fine.",
	"1, It seems so, yeah.",
	"0, OK, good.",
	"0, Yeah. Monitor her breathing.  Alert if it becomes irregular or stops.",
	"1, OK, my brother is is holding her neck and he's observing her breathing also.",
	"0, OK. And make sure she's kept still and does not move toward further injury.",
	"1, OK.",
	"0, I think the ambulance should be on its way, should be, should be there soon.",
	"1, Oh, that's good.",
	"1, Oh, that's good to hear.",
	"1, Yeah.",
	"0, And can you make sure nobody smokes near the accident site?",
	"1, I was feeling like having a smoker just now, OK?",
	"1, I'll wait.",
	"1, Oh the sirens.",
	"1, Oh, luckily there's coming.",
	"1, Someone who can help us? Thank you.",
	"1, Thank you.",
	"1, Bye bye.",
]
