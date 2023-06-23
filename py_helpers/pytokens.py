import os
import datetime
from datetime import timedelta, timezone
from fastapi import HTTPException
import jwt
from fastapi.security import HTTPBearer
from pytz import timezone


# Scheme for the Authorization header
token_auth_scheme = HTTPBearer()

TOKEN_SECRET = "eastvantage_token"
ENCRYPTION_ALGO = "HS256"
TOKEN_TYPE = "JWT"


def encode_token(payload_dict: object, expiry_secs: int) -> str:
	try:
		if payload_dict is None:
			payload_dict = {}
		if expiry_secs is not None:
			if "exp" not in payload_dict:
				# establish the access_token's validity ...
				# exp_dt = datetime.datetime.now(tz=timezone.utc) + timedelta(seconds=expiry_secs)
				exp_dt = datetime.datetime.now(timezone('Asia/Calcutta')) + timedelta(seconds=expiry_secs)
				payload_dict['exp'] = exp_dt
		encoded_token = jwt.encode(payload_dict, TOKEN_SECRET, algorithm=ENCRYPTION_ALGO)
	except Exception as e:
		print("encode_token: ***** ERROR ****")
		encoded_token = None
	return encoded_token


def decode_token(encoded_token: str) -> object:
	try:
		payload_dict = jwt.decode(encoded_token, TOKEN_SECRET, algorithms=[ENCRYPTION_ALGO])
	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=401, detail="Access Token has expired")
	except jwt.InvalidSignatureError:
		raise HTTPException(status_code=401, detail="Token signature does not match")
	except jwt.DecodeError:
		raise HTTPException(status_code=401, detail="Invalid token")
	return payload_dict


def check_token(token: str) -> tuple:
	'''
		If Authorization header is not found in the request, you will get a 403 Forbidden response
		If valid access_token in provided in the request, you will get 200 Response ok msg
		If expired access_token is provided in the request, you will get a 401 Unauthorized response
	'''
	# print("check_token: token.credentials=[" + str(token.credentials) + "]")
	payload_dict = decode_token(token.credentials)
	if payload_dict is not None:
		return True, payload_dict
	error_response = HTTPException(status_code=401, detail='Invalid token')
	return False, error_response
