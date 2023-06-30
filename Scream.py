# -*- coding: utf-8 -*-
import inspect

def RequestLoginRequest(ts,_guid,_key,_apiVersion,_regionId,_languageId):
	l= locals()
	l['CmdId']=0
	return l

def HelloRequest(ts,_agentToken):
	l= locals()
	l['CmdId']=1
	return l

def LoginUserRequest(ts,_romType,_platformId,_platformUserId,_countryCode,_currencyCode,_adId):
	l= locals()
	l['CmdId']=4119
	return l

def GetVersionRequest(ts):
	l= locals()
	l['CmdId']=4097
	return l

def GetStoryModeStatusVersionRequest(ts):
	l= locals()
	l['CmdId']=4448
	return l

def GetPremiumPassStatusRequest(ts):
	l= locals()
	l['CmdId']=5393
	return l

def GetStoryClearCountDayRequest(ts,_page):
	l= locals()
	l['CmdId']=4449
	return l

def GetAvailableVipIdListRequest(ts):
	l= locals()
	l['CmdId']=5385
	return l

def GetUserItemAndPointRequest(ts,_page):
	l= locals()
	l['CmdId']=4108
	return l

def CheckNewDayRequest(ts):
	l= locals()
	l['CmdId']=4113
	return l

def GetValueRequest(ts,_keys):
	l= locals()
	l['CmdId']=4109
	return l

def GetMissionSetInfoRequest(ts,_page):
	l= locals()
	l['CmdId']=5457
	return l

def GetHomeInfoRequest(ts):
	l= locals()
	l['CmdId']=4353
	return l

def GetPersonalMessageRequest(ts,_checkMessageId,_doNotShowAgain):
	l= locals()
	l['CmdId']=4370
	return l

def GetStoryTopInfoRequest(ts):
	l= locals()
	l['CmdId']=4436
	return l

def ReceivePresentBoxRequest(ts,presentBoxIds):
	l= locals()
	l['CmdId']=4355
	return l

def ExecuteShopItemGashaRequest(ts,_gashaId,_platformCode,_romType):
	l= locals()
	l['CmdId']=5397
	return l

def GetPresentBoxRequest(ts,_page):
	l= locals()
	l['CmdId']=4354
	return l

def GetStoryModeStatusRequest(ts,_page):
	l= locals()
	l['CmdId']=4440
	return l

def GetUserCharacterRequest(ts,_page):
	l= locals()
	l['CmdId']=4101
	return l

def GetPartyRequest(ts):
	l= locals()
	l['CmdId']=4112
	return l

def GetNotificationStatusRequest(ts):
	l= locals()
	l['CmdId']=4369
	return l

def GetMissionInfoRequest(ts,_missionSetIdList,_page):
	l= locals()
	l['CmdId']=5458
	return l

def GetStoryInfoRequest(ts,_storyType,_page):
	l= locals()
	l['CmdId']=4433
	return l

def GetMissionRewardRequest(ts,_missionIdList):
	l= locals()
	l['CmdId']=5459
	return l

def RecoverStaminaRequest(ts,_isUseStone,_useRecoverItem,_executionCount):
	l= locals()
	l['CmdId']=4438
	return l

def GetCompletedMissionRequest(ts,_omitConfirmFlg,_page):
	l= locals()
	l['CmdId']=5460
	return l

def GetResultStoryBattleRequest(ts,_battleResultKbn,_challengeDetailIdField,_sessionInfo,_missionUploadPageCnt):
	l= locals()
	l['CmdId']=4432
	return l

def PlayStoryBattleRequest(ts,_storyId,_partyId,_sallyCharacter1Id,_sallyCharacter2Id,_sallyCharacter3Id,_sallyCharacter4Id,_sallyCharacter5Id,_sallyCharacter6Id,_useTollStone,_useSkipTicket,_simpleBattle):
	l= locals()
	l['CmdId']=4434
	return l

def UserItemWT(_itemType,_itemId,_itemNum):
	l= locals()
	return l

def SessionInfo(_sessionKey):
	l= locals()
	return l