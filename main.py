# -*- coding: utf-8 -*-
import argparse
import socket
import ssl
import requests
import hashlib
import uuid
import time
import base64
import urllib
import json
import random
import threading
import io
import os
from pprint import pprint
import datetime
import codedbots
import Scream

def hexstring(array):
	return ''.join(format(x, '02x') for x in array)

def getip(host):
	return socket.gethostbyname(host)

def parseEcd(path,_platformId,_romType):
	with io.open(path,'rb') as f:
		return codedbots.codedbots().getecd(f.read(),_platformId,_romType)

class API(object):
	def __init__(self):
		self.host='ul2ahv9ohheiyu3t.dblgnds.channel.or.jp'
		self.port=0x85A2
		self.ts=0
		self.CmdId=None
		self.connect()
		self.prepare()
		self.codedbots=codedbots.codedbots()

	def prepare(self):
		with io.open(os.path.join('data','story_master_.json'),encoding='utf8') as f:
			self.story_master_=json.load(f)
			self.story_master_={x['story_master_id_']:x for x in self.story_master_}
		with io.open(os.path.join('data','tower_character_.json'),encoding='utf8') as f:
			self.tower_character_=json.load(f)
			self.tower_character_={x['story_master_id_']:x for x in self.tower_character_}
		with io.open(os.path.join('data','total_battle_level_.json'),encoding='utf8') as f:
			self.total_battle_level_=json.load(f)
			self.total_battle_level_={x['total_battle_id_']:x for x in self.total_battle_level_}
		with io.open(os.path.join('data','STORY-EPISODE-NAME.json'),encoding='utf8') as f:
			self.names={x['id']:x['text'] for x in json.load(f)['info']}
		with io.open(os.path.join('data','story_main_.json'),encoding='utf8') as f:
			self.story_main_=json.load(f)
			self.story_main_=sorted(self.story_main_, key = lambda x: (x['story_part_id_'], x['story_chapter_id_'], x['story_episode_id_']))
		with io.open(os.path.join('data','story_event_group_.json'),encoding='utf8') as f:
			self.story_event_group_=json.load(f)
			ts=time.time()
			tmp=[]
			for x in self.story_event_group_:
				end_date_=x['end_date_']
				tmp.append(x)
			self.story_event_group_=tmp
			self.story_event_group_={x['id_']:x for x in self.story_event_group_}

	def questname(self,quest):
		try:
			if 'story_part_id_' in quest:
				return 'Part.%s Book%s Chapter%s %s (%s)'%(quest['story_part_id_'],quest['story_chapter_id_'],quest['story_episode_id_'],self.names[quest['story_episode_name_id_']],quest['story_master_normal_id_'])
			else:
				return 'Chapter%s %s (%s)'%(quest['story_event_episode_id_'],self.names[quest['story_event_episode_name_id_']],quest['story_event_story_master_normal_id_'])
		except:
			return 'missing name for %s'%(quest['id_'])

	def getStory(self,story_master_id_):
		if story_master_id_ in self.story_master_:
			return self.story_master_[story_master_id_]
		return None

	def log(self,msg):
		if hasattr(self,'debug'):
			print('[%s] %s'%(time.strftime('%H:%M:%S'),msg))

	def connect(self,ip=None):
		if not ip:
			self.ip=getip(self.host)
		if hasattr(self,'s'):
			self.s.close()
		self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.settimeout(10)
		context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
		context.check_hostname = False
		context.verify_mode = ssl.CERT_NONE
		self.s=ssl.SSLContext.wrap_socket(context,self.s)
		if not ip:
			ip=getip(self.host)
		self.log('connecting ip:%s port:%s'%(ip,self.port))
		self.s.connect((ip,self.port))

	def dodecode(self,data):
		return Scream.tools.Decode(data)

	def decode(self,reader,bt):
		_cmdId = reader['CmdId']
		if _cmdId==144:
			return self.makepacket(bt)
		if False:
			if self.__cmdId:
				if self.__cmdId!=_cmdId:
					self.ts+=1
			if not self.__cmdId:
				self.__cmdId=_cmdId
		if _cmdId!=self.CmdId:
			return self.makepacket(bt)
		r=reader
		if '_token' in r:
			self._token=r['_token']
		if '_userStatus' in r:
			self._userStatus=r['_userStatus']
		if '_stoneStatus' in r:
			self._stoneStatus=r['_stoneStatus']
		if '_zeny' in r:
			self._zeny=r['_zeny']
		if _cmdId == 0:
			self.ip=r['ip']
			self.log('new ip: %s port: %s'%(self.ip,r['port']))
			self.connect(self.ip)
		return r

	def makepacket(self,bt):
		if self.CmdId is not None:
			if self.CmdId!=bt['CmdId']:
				self.ts+=1
		self.CmdId=bt['CmdId']
		_bt=self.codedbots.encrypt(bt)
		self.s.send(_bt)
		data = self.s.recv(0xFFFF)
		res=self.codedbots.decrypt(data)
		return self.decode(res,bt)

	def GetMissionRewardRequest(self,_missionIdList):
		bt=Scream.GetMissionRewardRequest(self.ts,_missionIdList)
		return self.makepacket(bt)

	def SendCapyVerificationRequest(self,_encrypted,_signature):
		bt=Scream.SendCapyVerificationRequest(self.ts,_encrypted,_signature)
		return self.makepacket(bt)

	def RequestLoginRequest(self,_guid,_key,_apiVersion,_regionId,_languageId):
		bt=Scream.RequestLoginRequest(self.ts,_guid,_key,_apiVersion,_regionId,_languageId)
		return self.makepacket(bt)

	def HelloRequest(self,_agentToken):
		self.ts=1
		bt=Scream.HelloRequest(self.ts,_agentToken)
		return self.makepacket(bt)

	def GetVipPackageListRequest(self,_page):
		bt=Scream.GetVipPackageListRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetPresentBoxRequest(self,_page):
		bt=Scream.GetPresentBoxRequest(self.ts,_page)
		return self.makepacket(bt)

	def getallmail(self):
		box=self.GetPresentBoxRequest(1)
		_presentBoxIds=[]
		for x in box['_presentBoxList']:
			_presentBoxIds.append(x['_presentBoxId'])
		if len(_presentBoxIds)>=1:
			self.ReceivePresentBoxRequest(_presentBoxIds)

	def GetPresentBoxHistoryRequest(self,_page):
		bt=Scream.GetPresentBoxHistoryRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetCustomMessageRequest(self,_customMessageId):
		bt=Scream.GetCustomMessageRequest(self.ts,_customMessageId)
		return self.makepacket(bt)

	def CreateUserRequest(self,_romType,_platformId,_platformUserId,_countryCode,_currencyCode,_adId):
		bt=Scream.CreateUserRequest(self.ts,_romType,_platformId,_platformUserId,_countryCode,_currencyCode,_adId)
		return self.makepacket(bt)

	def GetUserCodeRequest(self):
		bt=Scream.GetUserCodeRequest(self.ts)
		return self.makepacket(bt)

	def GetUserArtsBoostBaseRequest(self,_page):
		bt=Scream.GetUserArtsBoostBaseRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetItemPackListRequest(self,_page):
		bt=Scream.GetItemPackListRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetBoxGashaInfoRequest(self,_gashaSeriesId):
		bt=Scream.GetBoxGashaInfoRequest(self.ts,_gashaSeriesId)
		return self.makepacket(bt)

	def ExecuteRouletteGashaRequest(self,_gashaPackId,_count):
		bt=Scream.ExecuteRouletteGashaRequest(self.ts,_gashaPackId,_count)
		return self.makepacket(bt)

	def RegisterBnIdRequest(self,_romRegion,_code):
		bt=Scream.RegisterBnIdRequest(self.ts,_romRegion,String(_code))
		return self.makepacket(bt)

	def SetOptionsRequest(self,_userSetting):
		bt=Scream.SetOptionsRequest(self.ts,_userSetting)
		return self.makepacket(bt)

	def SetValueRequest(self,_keyname,_value):
		bt=Scream.SetValueRequest(self.ts,_keyname,_value)
		return self.makepacket(bt)

	def GetStoryModeStatusVersionRequest(self):
		bt=Scream.GetStoryModeStatusVersionRequest(self.ts)
		return self.makepacket(bt)

	def GetPremiumPassStatusRequest(self):
		bt=Scream.GetPremiumPassStatusRequest(self.ts)
		return self.makepacket(bt)

	def GetUserEquipmentRequest(self,_page):
		bt=Scream.GetUserEquipmentRequest(self.ts,_page)
		return self.makepacket(bt)
		return res

	def GetUserCharacterRequest(self,_page):
		bt=Scream.GetUserCharacterRequest(self.ts,_page)
		return self.makepacket(bt)

	def getAllChars(self):
		_page=1
		self._characterIds=set()
		while(1):
			res=self.GetUserCharacterRequest(_page)
			if res['_pageSize']<=0:	break
			for x in res['_items']:
				self._characterIds.add(x['_characterId'])
			_page+=1
		return self._characterIds

	def exportChars(self):
		res=set()
		with io.open(os.path.join('data','character_property_master_.json'),encoding='utf8') as f:
			self.character_property_master_=json.load(f)
			self.character_property_master_={x['character_id_']:x for x in self.character_property_master_}
		have=self.getAllChars()
		for x in have:
			if x in self.character_property_master_:
				if self.character_property_master_[x]['character_rarity_']>=2:
					res.add(x)
		return res

	def GetStoryModeStatusRequest(self,_page):
		bt=Scream.GetStoryModeStatusRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetPartyRequest(self):
		bt=Scream.GetPartyRequest(self.ts)
		return self.makepacket(bt)

	def GetUserShardRequest(self,_page):
		bt=Scream.GetUserShardRequest(self.ts,_page)
		return self.makepacket(bt)

	def CheckAliveRequest(self):
		bt=Scream.CheckAliveRequest(self.ts)
		return self.makepacket(bt)

	def CompleteDispatchRequest(self,_dlIdList,_dispatchTimeSaveList):
		bt=Scream.CompleteDispatchRequest(self.ts,_dlIdList,_dispatchTimeSaveList)
		return self.makepacket(bt)

	def StartTrainingRequest(self,_trainingSpotId,_trainingCharacterId,_trainingPartnerCharacter1Id,_trainingPartnerCharacter2Id,_trainingPartnerCharacter3Id,_trainingPartnerCharacter4Id,_trainingPartnerCharacter5Id,_artsId):
		bt=Scream.StartTrainingRequest(self.ts,_trainingSpotId,_trainingCharacterId,_trainingPartnerCharacter1Id,_trainingPartnerCharacter2Id,_trainingPartnerCharacter3Id,_trainingPartnerCharacter4Id,_trainingPartnerCharacter5Id,_artsId)
		return self.makepacket(bt)

	def GetResultTrainingRequest(self,_trainingResultRequestList):
		bt=Scream.GetResultTrainingRequest(self.ts,_trainingResultRequestList)
		return self.makepacket(bt)

	def UnlockBoostPanelRequest(self,_characterId,_classId,_panelIdList,_stoneFlg):
		bt=Scream.UnlockBoostPanelRequest(self.ts,_characterId,_classId,_panelIdList,_stoneFlg)
		return self.makepacket(bt)

	def UnlockBoostBoardRequest(self,_characterId,_boardId,_stoneFlg):
		bt=Scream.UnlockBoostBoardRequest(self.ts,_characterId,_boardId,_stoneFlg)
		return self.makepacket(bt)

	def GetUserAvatarRequest(self,_page):
		bt=Scream.GetUserAvatarRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetUserGashaTicketRequest(self):
		bt=Scream.GetUserGashaTicketRequest(self.ts)
		return self.makepacket(bt)

	def GetUserSoulRequest(self):
		bt=Scream.GetUserSoulRequest(self.ts)
		return self.makepacket(bt)

	def GetUserTrainingItemRequest(self):
		bt=Scream.GetUserTrainingItemRequest(self.ts)
		return self.makepacket(bt)

	def GetUserPieceRequest(self):
		bt=Scream.GetUserPieceRequest(self.ts)
		return self.makepacket(bt)

	def GetUserGeneralItemRequest(self,_page):
		bt=Scream.GetUserGeneralItemRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetAvatarRequest(self):
		bt=Scream.GetAvatarRequest(self.ts)
		return self.makepacket(bt)

	def GetUserStaminaRecoverItemRequest(self):
		bt=Scream.GetUserStaminaRecoverItemRequest(self.ts)
		return self.makepacket(bt)

	def GetUserEquipmentBlueprintRequest(self):
		bt=Scream.GetUserEquipmentBlueprintRequest(self.ts)
		return self.makepacket(bt)

	def GetUserDragonballRequest(self):
		bt=Scream.GetUserDragonballRequest(self.ts)
		return self.makepacket(bt)

	def GetUserMultiShardRequest(self):
		bt=Scream.GetUserMultiShardRequest(self.ts)
		return self.makepacket(bt)

	def GetUserAwakenShardRequest(self,_page):
		bt=Scream.GetUserAwakenShardRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetCooperateBattleStageStatusRequest(self,_cooperateLevelId):
		bt=Scream.GetCooperateBattleStageStatusRequest(self.ts,_cooperateLevelId)
		return self.makepacket(bt)

	def GetStoryClearCountRequest(self,_storyMasterIds):
		bt=Scream.GetStoryClearCountRequest(self.ts,_storyMasterIds)
		return self.makepacket(bt)

	def ReceivePresentBoxRequest(self,presentBoxIds):
		bt=Scream.ReceivePresentBoxRequest(self.ts,presentBoxIds)
		return self.makepacket(bt)

	def GetCoopRaidBossHealthRequest(self,_storyMasterId):
		bt=Scream.GetCoopRaidBossHealthRequest(self.ts,_storyMasterId)
		return self.makepacket(bt)

	def GetMedalShopItemListRequest(self,_page):
		bt=Scream.GetMedalShopItemListRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetFamousCharacterRequest(self,_gameMode,_gameModeBranch):
		bt=Scream.GetFamousCharacterRequest(self.ts,_gameMode,_gameModeBranch)
		return self.makepacket(bt)

	def GetShopItemListRequest(self,_page,_platformCode,_romType):
		bt=Scream.GetShopItemListRequest(self.ts,_page,_platformCode,_romType)
		return self.makepacket(bt)

	def GetNotificationStatusRequest(self):
		bt=Scream.GetNotificationStatusRequest(self.ts)
		return self.makepacket(bt)

	def GetZenkaiGashaInfoRequest(self,_page):
		bt=Scream.GetZenkaiGashaInfoRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetStartDashGashaInfoRequest(self,_page):
		bt=Scream.GetStartDashGashaInfoRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetValueRequest(self,_keys):
		bt=Scream.GetValueRequest(self.ts,_keys)
		return self.makepacket(bt)

	def GetUserTitleRequest(self,_page):
		bt=Scream.GetUserTitleRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetUserBattleMessageRequest(self):
		bt=Scream.GetUserBattleMessageRequest(self.ts)
		return self.makepacket(bt)

	def GetAvailableVipIdListRequest(self):
		bt=Scream.GetAvailableVipIdListRequest(self.ts)
		return self.makepacket(bt)

	def GetUserItemAndPointRequest(self,_page):
		bt=Scream.GetUserItemAndPointRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetTrainingSpotRequest(self,_trainingType,_page):
		bt=Scream.GetTrainingSpotRequest(self.ts,_trainingType,_page)
		return self.makepacket(bt)

	def GetDispatchInfoRequest(self):
		bt=Scream.GetDispatchInfoRequest(self.ts)
		return self.makepacket(bt)

	def GetCooperatePartyInfoRequest(self):
		bt=Scream.GetCooperatePartyInfoRequest(self.ts)
		return self.makepacket(bt)

	def UpdateCooperatePartyInfoRequest(self,_battleCharacterId,_battleCharacterEquipment1InsId,_battleCharacterEquipment2InsId,_battleCharacterEquipment3InsId,_subCharacter1Id,_subCharacter2Id,_subCharacter3Id,_subCharacter4Id,_subCharacter5Id,_subCharacter6Id,_subCharacter7Id,_subCharacter8Id,_subCharacter9Id,_subCharacter10Id):
		bt=Scream.UpdateCooperatePartyInfoRequest(self.ts,_battleCharacterId,_battleCharacterEquipment1InsId,_battleCharacterEquipment2InsId,_battleCharacterEquipment3InsId,_subCharacter1Id,_subCharacter2Id,_subCharacter3Id,_subCharacter4Id,_subCharacter5Id,_subCharacter6Id,_subCharacter7Id,_subCharacter8Id,_subCharacter9Id,_subCharacter10Id)
		return self.makepacket(bt)

	def GetCoopRaidPartyInfoRequest(self):
		bt=Scream.GetCoopRaidPartyInfoRequest(self.ts)
		return self.makepacket(bt)

	def UpdateCoopRaidPartyInfoRequest(self,_battleCharacterId,_battleCharacterEquipment1InsId,_battleCharacterEquipment2InsId,_battleCharacterEquipment3InsId,_subCharacter1Id,_subCharacter2Id,_subCharacter3Id,_subCharacter4Id,_subCharacter5Id,_subCharacter6Id,_subCharacter7Id,_subCharacter8Id,_subCharacter9Id,_subCharacter10Id):
		bt=Scream.UpdateCoopRaidPartyInfoRequest(self.ts,_battleCharacterId,_battleCharacterEquipment1InsId,_battleCharacterEquipment2InsId,_battleCharacterEquipment3InsId,_subCharacter1Id,_subCharacter2Id,_subCharacter3Id,_subCharacter4Id,_subCharacter5Id,_subCharacter6Id,_subCharacter7Id,_subCharacter8Id,_subCharacter9Id,_subCharacter10Id)
		return self.makepacket(bt)

	def PlayStoryBattleRequest(self,_storyId,_partyId,_sallyCharacter1Id,_sallyCharacter2Id,_sallyCharacter3Id,_sallyCharacter4Id,_sallyCharacter5Id,_sallyCharacter6Id,_useTollStone,_useSkipTicket,_simpleBattle):
		bt=Scream.PlayStoryBattleRequest(self.ts,_storyId,_partyId,_sallyCharacter1Id,_sallyCharacter2Id,_sallyCharacter3Id,_sallyCharacter4Id,_sallyCharacter5Id,_sallyCharacter6Id,_useTollStone,_useSkipTicket,_simpleBattle)
		return self.makepacket(bt)

	def GetResultStoryBattleRequest(self,_battleResultKbn,_challengeDetailIdField,_sessionInfo,_missionUploadPageCnt):
		bt=Scream.GetResultStoryBattleRequest(self.ts,_battleResultKbn,_challengeDetailIdField,_sessionInfo,_missionUploadPageCnt)
		return self.makepacket(bt)

	def GetVersionRequest(self):
		bt=Scream.GetVersionRequest(self.ts)
		return self.makepacket(bt)

	def GetStoryTopInfoRequest(self):
		bt=Scream.GetStoryTopInfoRequest(self.ts)
		return self.makepacket(bt)

	def GetStoryInfoRequest(self,_storyType,_page):
		bt=Scream.GetStoryInfoRequest(self.ts,_storyType,_page)
		return self.makepacket(bt)

	def GetGashaInfoRequest(self,_page):
		bt=Scream.GetGashaInfoRequest(self.ts,_page)
		return self.makepacket(bt)

	def getFreeGacha(self):
		with io.open(os.path.join('data','gasha_pack_.json'),encoding='utf8') as f:
			self.gasha_pack_=json.load(f)
			self.gasha_pack_={x['gasha_series_id_']:x for x in self.gasha_pack_}
		_gashaInfoList=self.GetGashaInfoRequest(1)._gashaInfoList
		for x in _gashaInfoList:
			if x._gashaSeriesId in self.gasha_pack_:
				if self.gasha_pack_[x._gashaSeriesId]['consume_item_type_']==9:
					while(1):
						_consumeItem=self.ExecuteGashaRequest(_gashaId=x._gashaPackId)._consumeItem
						if _consumeItem._itemId==0:
							break

	def ExecuteGashaRequest(self,_gashaId):
		bt=Scream.ExecuteGashaRequest(self.ts,_gashaId)
		return self.makepacket(bt)

	def UpdatePartyInfoRequest(self,_partyInfo):
		bt=Scream.UpdatePartyInfoRequest(self.ts,_partyInfo)
		return self.makepacket(bt)

	def UpdateFavoriteCharacterRequest(self,_characterId):
		bt=Scream.UpdateFavoriteCharacterRequest(self.ts,_characterId)
		return self.makepacket(bt)

	def UpdateUserNameRequest(self,_playerName):
		bt=Scream.UpdateUserNameRequest(self.ts,_playerName)
		return self.makepacket(bt)

	def CheckNewDayRequest(self):
		bt=Scream.CheckNewDayRequest(self.ts)
		return self.makepacket(bt)

	def GetLimitedLoginBonusRequest(self,_loginBonusEventId,_page):
		bt=Scream.GetLimitedLoginBonusRequest(self.ts,_loginBonusEventId,_page)
		return self.makepacket(bt)

	def SetNextLoginBonusItemRequest(self,_nextLoginBonusItemList):
		bt=Scream.SetNextLoginBonusItemRequest(self.ts,_nextLoginBonusItemList)
		return self.makepacket(bt)

	def GetMissionSetInfoRequest(self,_page):
		bt=Scream.GetMissionSetInfoRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetMissionInfoRequest(self,_missionSetIdList,_page):
		bt=Scream.GetMissionInfoRequest(self.ts,_missionSetIdList,_page)
		return self.makepacket(bt)

	def GetMissionGainInfoRequest(self,_missionSetIdList,_page):
		bt=Scream.GetMissionGainInfoRequest(self.ts,_missionSetIdList,_page)
		return self.makepacket(bt)

	def GetHomeInfoRequest(self):
		bt=Scream.GetHomeInfoRequest(self.ts)
		return self.makepacket(bt)

	def GetCompletedMissionRequest(self,_omitConfirmFlg,_page):
		bt=Scream.GetCompletedMissionRequest(self.ts,_omitConfirmFlg,_page)
		return self.makepacket(bt)

	def GetPersonalMessageRequest(self,_checkMessageId,_doNotShowAgain):
		bt=Scream.GetPersonalMessageRequest(self.ts,_checkMessageId,_doNotShowAgain)
		return self.makepacket(bt)

	def LoginUserRequest(self,_romType,_platformId,_platformUserId,_countryCode,_currencyCode,_adId):
		bt=Scream.LoginUserRequest(self.ts,_romType,_platformId,_platformUserId,_countryCode,_currencyCode,_adId)
		return self.makepacket(bt)

	def GetStoryClearCountDayRequest(self,_page):
		bt=Scream.GetStoryClearCountDayRequest(self.ts,_page)
		return self.makepacket(bt)

	def ExecuteShopItemGashaRequest(self,_gashaId,_platformCode,_romType):
		bt=Scream.ExecuteShopItemGashaRequest(self.ts,_gashaId,_platformCode,_romType)
		return self.makepacket(bt)

	def GetMissionPlanStatusRequest(self):
		bt=Scream.GetMissionPlanStatusRequest(self.ts)
		return self.makepacket(bt)

	def UploadMissionProgressBulkRequest(self,_page,_storyId,_missionProgressList):
		bt=Scream.UploadMissionProgressBulkRequest(self.ts,_page,_storyId,_missionProgressList)
		return self.makepacket(bt)

	def GetUserEquipmentByIdRequest(self,_equipmentInsIds):
		bt=Scream.GetUserEquipmentByIdRequest(self.ts,_equipmentInsIds)
		return self.makepacket(bt)

	def GetGashaInfoByIdRequest(self,_page,_gashaSeriesIdList):
		bt=Scream.GetGashaInfoByIdRequest(self.ts,_page,_gashaSeriesIdList)
		return self.makepacket(bt)

	def GetOverallRankingTopInfoRequest(self):
		bt=Scream.GetOverallRankingTopInfoRequest(self.ts)
		return self.makepacket(bt)

	def GetDop4PartyRequest(self,_storyMasterId):
		bt=Scream.GetDop4PartyRequest(self.ts,_storyMasterId)
		return self.makepacket(bt)

	def TradeMedalItemRequest(self,_medalShopItemId,_tradeCount):
		bt=Scream.TradeMedalItemRequest(self.ts,_medalShopItemId,_tradeCount)
		return self.makepacket(bt)

	def UnlockEquipmentRequest(self,_equipmentInsIds,_stoneFlg):
		bt=Scream.UnlockEquipmentRequest(self.ts,_equipmentInsIds,_stoneFlg)
		return self.makepacket(bt)

	def UpdateMissionProgressRequest(self,_missionProgressList,_storyId):
		bt=Scream.UpdateMissionProgressRequest(self.ts,_missionProgressList,_storyId)
		return self.makepacket(bt)

	def SetMissionPlanRequest(self,_missionPlanId):
		bt=Scream.SetMissionPlanRequest(self.ts,_missionPlanId)
		return self.makepacket(bt)

	def GetUserUnlockItemRequest(self,_page):
		bt=Scream.GetUserUnlockItemRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetOverallRankingSeasonRewardRequest(self):
		bt=Scream.GetOverallRankingSeasonRewardRequest(self.ts)
		return self.makepacket(bt)

	def RecoverStaminaRequest(self,_isUseStone,_useRecoverItem,_executionCount):
		bt=Scream.RecoverStaminaRequest(self.ts,_isUseStone,_useRecoverItem,_executionCount)
		return self.makepacket(bt)

	def UserItemWT(self,_itemType,_itemId,_itemNum):
		return Scream.UserItemWT(_itemType,_itemId,_itemNum)

	def OpenItemPackRequest(self,_itemPackId,_count):
		bt=Scream.OpenItemPackRequest(self.ts,_itemPackId,_count)
		return self.makepacket(bt)

	def GetTactSeasonRewardRequest(self,_seasonId,_rankGrade):
		bt=Scream.GetTactSeasonRewardRequest(self.ts,_seasonId,_rankGrade)
		return self.makepacket(bt)

	def TactTopInfoRequest(self):
		bt=Scream.TactTopInfoRequest(self.ts)
		return self.makepacket(bt)

	def GetTactBattleHistoryRequest(self,_page):
		bt=Scream.GetTactBattleHistoryRequest(self.ts,_page)
		return self.makepacket(bt)

	def GetTactPartyRequest(self,_mapId,_nodeId):
		bt=Scream.GetTactPartyRequest(self.ts,_mapId,_nodeId)
		return self.makepacket(bt)

	def GetCooperateEventRequest(self):
		bt=Scream.GetCooperateEventRequest(self.ts)
		return self.makepacket(bt)

	def CheckBattleSessionRequest(self,_battleType,_sessionInfo):
		bt=Scream.CheckBattleSessionRequest(self.ts,_battleType,_sessionInfo)
		return self.makepacket(bt)

	def GetTotalBattleLevelListRequest(self,_totalBattleId):
		bt=Scream.GetTotalBattleLevelListRequest(self.ts,_totalBattleId)
		return self.makepacket(bt)

	def GetTotalBattleLevelInfoRequest(self,_totalBattleLevelId):
		bt=Scream.GetTotalBattleLevelInfoRequest(self.ts,_totalBattleLevelId)
		return self.makepacket(bt)

	def GetTotalBattleLayerInfoRequest(self,_totalBattleLevelId,_totalBattleLayerId):
		bt=Scream.GetTotalBattleLayerInfoRequest(self.ts,_totalBattleLevelId,_totalBattleLayerId)
		return self.makepacket(bt)

	def PlayTotalBattleRequest(self,_totalBattleLevelId,_totalBattleLayerId,_sallyCharacter1Id,_sallyCharacter2Id,_sallyCharacter3Id,_sallyCharacter4Id,_sallyCharacter5Id,_sallyCharacter6Id,_battleCharacterIdList):
		bt=Scream.PlayTotalBattleRequest(self.ts,_totalBattleLevelId,_totalBattleLayerId,_sallyCharacter1Id,_sallyCharacter2Id,_sallyCharacter3Id,_sallyCharacter4Id,_sallyCharacter5Id,_sallyCharacter6Id,_battleCharacterIdList)
		return self.makepacket(bt)

	def GetResultTotalBattleRequest(self,_sessionInfo,_battleResultKbn,_challenge1Cleared,_challenge2Cleared,_challenge3Cleared,_challenge4Cleared,_challenge5Cleared,_challenge6Cleared,_challenge7Cleared,_enemyPartyInfo,_missionUploadPageCnt):
		bt=Scream.GetResultTotalBattleRequest(self.ts,_sessionInfo,_battleResultKbn,_challenge1Cleared,_challenge2Cleared,_challenge3Cleared,_challenge4Cleared,_challenge5Cleared,_challenge6Cleared,_challenge7Cleared,_enemyPartyInfo,_missionUploadPageCnt)
		return self.makepacket(bt)

	def GetWorldMissionInfoRequest(self,_page):
		bt=Scream.GetWorldMissionInfoRequest(self.ts,_page)
		return self.makepacket(bt)

	def SellEquipmentRequest(self,_equipmentInsIds):
		bt=Scream.SellEquipmentRequest(self.ts,_equipmentInsIds)
		return self.makepacket(bt)

	def GetCoopRaidOverallRewardRequest(self,_storyMasterId):
		bt=Scream.GetCoopRaidOverallRewardRequest(self.ts,_storyMasterId)
		return self.makepacket(bt)

	def GetBattleMessageRequest(self,_page,_battleTypes):
		bt=Scream.GetBattleMessageRequest(self.ts,_page,_battleTypes)
		return self.makepacket(bt)

	def UnlockBoostBoardBulkRequest(self,_characterId,_boardList):
		bt=Scream.UnlockBoostBoardBulkRequest(self.ts,_characterId,_boardList)
		return self.makepacket(bt)

	def setRegion(self,r='EU'):
		self._regionId=r

	def setLanguage(self,r='EN'):
		self._languageId=r

	def setRom(self,r=2):
		self._romType=int(r)

	def setPlatform(self,r=2):
		self._platformId=int(r)

	def getShopItems(self):
		page=1
		items=[]
		while(1):
			if page>=5:	break
			res=self.GetShopItemListRequest(_page=page,_platformCode=2,_romType=2)
			if res['_pageSize']<=0:	break
			for x in res._shopItemList:
				items.append(x)
			page+=1
		return items

	def getFinishedQuests(self):
		page=1
		self.done=set()
		while(1):
			res=self.GetStoryModeStatusRequest(_page=page)
			if res['_pageSize']<=0:	break
			for x in res['_storyModeStatusList']:
				v0=self.getStory(x['_storyMasterId'])
				if not v0:	continue
				if (int(x['_currentChallengeDetailIdList'])==1111111) or (v0['battle_type_']==0 and x['_clearCountTotal']>=1):
					self.done.add(x['_storyMasterId'])
			page+=1
		return self.done

	def getLeader(self,forbidden=set(),needParty=False):
		party=self.GetPartyRequest()
		if '_partyInfos' not in party:
			return self.getLeader(forbidden)
		if needParty:
			return [x['_characterId'] for x in party['_partyInfos'][0]['_partyCharacters']]
		for x in party['_partyInfos'][0]['_partyCharacters']:
			if x['_characterId'] not in forbidden:
				return x['_characterId']

	def doallquests(self,canRefill=True,isHard=False):
		self.getFinishedQuests()
		if not hasattr(self,'_characterIds'):
			self.getAllChars()
		_characterId=self.getLeader()
		self.log('will use _characterId %s'%_characterId)
		for y in self.story_main_:
			for j in y:
				if 'story_master_' not in j:	continue
				if isHard and '_normal_' in j:	continue
				if not isHard and '_normal_' not in j:	continue
				x=y[j]
				if x==-1:	continue
				if x in self.done:	break
				v0=self.getStory(x)
				if not v0:	continue
				story_unlock_param1_=v0['story_unlock_param1_']
				if v0['story_sorty1_id_']==10:
					_characterId=self.getLeader(set([v0['story_sorty1_param1_'],v0['story_sorty1_param2_'],v0['story_sorty1_param3_'],]))
					self.log('new _characterId %s'%_characterId)
				if canRefill:
					self.RecoverStaminaRequest(_isUseStone=0,_useRecoverItem=self.UserItemWT(_itemType=31,_itemId=0,_itemNum=1),_executionCount=0)
				self.log('doing %s'%(self.questname(y)))
				res=self.doquest(x,_characterId,False)

	def doallevents(self,canRefill=True,isHard=False):
		self.getFinishedQuests()
		if not hasattr(self,'_characterIds'):
			self.getAllChars()
		_characterId=self.getLeader()
		self.log('will use _characterId %s'%_characterId)
		storyres=[]
		_page=1
		while(1):
			tmp=self.GetStoryInfoRequest(_storyType=2,_page=_page)
			if len(tmp['_storyInfoList'])<=0:	break
			for j in tmp['_storyInfoList']:
				storyres.append(j)
			_page+=1
		story_event_group_=set()
		for j in storyres:
			if j['_unlockStatus']!=0:
				continue
			story_event_group_.add(j['_id'])
		bad=set()
		for y in story_event_group_:
			if y not in self.story_event_group_:
				continue
			if y in self.total_battle_level_:
				continue
				self.canloop=True
				_levelInfoList=self.GetTotalBattleLevelListRequest(_totalBattleId=y)._levelInfoList
				for q in list(reversed(_levelInfoList)):
					if q._isCleared:	continue
					if not q._isReleased:	continue
					print(q._totalBattleLevelId,q._targetTotalBattleLayerId)
					self.GetTotalBattleLevelInfoRequest(q._totalBattleLevelId)
					self.GetTotalBattleLayerInfoRequest(q._totalBattleLevelId,q._targetTotalBattleLayerId)
					res=self.doquest(q._totalBattleLevelId,_characterId,False,q._targetTotalBattleLayerId)
					exit(1)
			y=self.story_event_group_[y]
			for j in y:
				if 'story_event_story_master_' not in j:
					continue
				if isHard and '_normal_' in j:
					continue
				if not isHard and '_normal_' not in j:
					continue
				x=y[j]
				if x==-1:
					continue
				if x not in self.tower_character_ and x in self.done:	break
				v0=self.getStory(x)
				if not v0:
					continue
				story_unlock_param1_=v0['story_unlock_param1_']
				if v0['story_sorty1_id_']==10:
					_characterId=self.getLeader(set([v0['story_sorty1_param1_'],v0['story_sorty1_param2_'],v0['story_sorty1_param3_'],]))
					self.log('new _characterId %s'%_characterId)
				elif v0['story_sorty1_id_'] in set([9999]):#4,7]):
					story_sorty1_param1_=int(str(v0['story_sorty1_param1_']).split('60')[-1])
					if story_sorty1_param1_ in self._characterIds:
						_characterId=story_sorty1_param1_
						self.UpdatePartyInfoRequest(_partyInfo=self.PartyInfo(_partyId=0,_partyName='Party1',_partyCharacters=[self.PartyCharacterEquipmentInfo(_characterId=_characterId,_partyMemberId=1,_equipmentInsIds=[-1,-1,-1]),self.PartyCharacterEquipmentInfo(_characterId=-1,_partyMemberId=2,_equipmentInsIds=[-1,-1,-1]),self.PartyCharacterEquipmentInfo(_characterId=-1,_partyMemberId=3,_equipmentInsIds=[-1,-1,-1]),self.PartyCharacterEquipmentInfo(_characterId=-1,_partyMemberId=4,_equipmentInsIds=[-1,-1,-1]),self.PartyCharacterEquipmentInfo(_characterId=-1,_partyMemberId=5,_equipmentInsIds=[-1,-1,-1]),self.PartyCharacterEquipmentInfo(_characterId=-1,_partyMemberId=6,_equipmentInsIds=[-1,-1,-1])]))
						self.log('new _characterId %s'%_characterId)
					else:
						continue
				if canRefill:
					self.RecoverStaminaRequest(_isUseStone=0,_useRecoverItem=self.UserItemWT(_itemType=31,_itemId=0,_itemNum=1),_executionCount=0)
				self.log('doing %s'%(self.questname(y)))
				if x in self.tower_character_:
					for _ in range(100):
						if not self.doquest(x,_characterId,False):
							break
				else:
					res=self.doquest(x,_characterId,False)
				if not res:
					bad.add(y['story_event_group_id_'])

	def doquest(self,_storyId=10010205,_characterId=None,canRefill=False,_totalBattleLayerId=None):
		if _characterId is None:
			_characterId=self.getLeader()
		if _totalBattleLayerId is None:
			v0=self.getStory(_storyId)
			if not v0:
				return None
			if v0['battle_type_']==1:
				_challengeDetailIdField=1111111
			else:
				_challengeDetailIdField=0
		if _storyId in self.tower_character_:
			_challengeDetailIdField=0
		if _totalBattleLayerId is not None:
			res=self.PlayTotalBattleRequest(_totalBattleLevelId=_storyId,_totalBattleLayerId=_totalBattleLayerId,_sallyCharacter1Id=495,_sallyCharacter2Id=524,_sallyCharacter3Id=38,_sallyCharacter4Id=4,_sallyCharacter5Id=46,_sallyCharacter6Id=-1,_battleCharacterIdList=[495,524,38])
		else:
			res=self.PlayStoryBattleRequest(_storyId=_storyId,_partyId=0,_sallyCharacter1Id=_characterId,_sallyCharacter2Id=-1,_sallyCharacter3Id=-1,_sallyCharacter4Id=-1,_sallyCharacter5Id=-1,_sallyCharacter6Id=-1,_useTollStone=0,_useSkipTicket=0,_simpleBattle=0)
		if '_sessionInfo' not in res:
			return self.doquest(_storyId,_characterId,canRefill)
		_sessionKey=res['_sessionInfo']['_sessionKey']
		if len(_sessionKey)<=0:
			if canRefill:
				self.RecoverStaminaRequest(_isUseStone=0,_useRecoverItem=self.UserItemWT(_itemType=31,_itemId=0,_itemNum=1),_executionCount=0)
				return self.doquest(_storyId,_characterId)
			else:
				return None
		self.log('_sessionKey: %s'%(_sessionKey))
		time.sleep(5)
		if _totalBattleLayerId is not None:
			time.sleep(4)
			res=self.GetResultTotalBattleRequest(_sessionInfo=self.SessionInfo(_sessionKey=_sessionKey),_battleResultKbn=1,_challenge1Cleared=1,_challenge2Cleared=1,_challenge3Cleared=1,_challenge4Cleared=1,_challenge5Cleared=1,_challenge6Cleared=1,_challenge7Cleared=1,_enemyPartyInfo=self.TotalBattlePartyInfo(_enemyCharacter1Health=0,_enemyCharacter2Health=-1,_enemyCharacter3Health=-1,_enemyCharacter4Health=-1,_enemyCharacter5Health=-1,_enemyCharacter6Health=-1),_missionUploadPageCnt=-1)
		else:
			res=self.GetResultStoryBattleRequest(_battleResultKbn=1,_challengeDetailIdField=_challengeDetailIdField,_sessionInfo=self.SessionInfo(_sessionKey=_sessionKey),_missionUploadPageCnt=-1)
		self.GetVersionRequest()
		self.GetStoryTopInfoRequest()
		self.GetCompletedMissionRequest(_omitConfirmFlg=1,_page=1)
		self.GetNotificationStatusRequest()
		self.done.add(_storyId)
		return res

	def login(self,guid,key):
		guid=self.codedbots.getuuid(guid)
		key=self.codedbots.getuuid(key)
		self.log('guid: %s key: %s'%(hexstring(guid),hexstring(key)))
		self.RequestLoginRequest(_guid=base64.b64encode(guid).decode(),_key=base64.b64encode(key).decode(),_apiVersion=274,_regionId=self._regionId,_languageId=self._languageId)
		self.log('_token: %s'%(hexstring(base64.b64decode(self._token))))
		self.HelloRequest(_agentToken=self._token)
		self.LoginUserRequest(_romType=self._romType,_platformId=self._platformId,_platformUserId='00000000-0000-0000-0000-000000000000',_countryCode='DE',_currencyCode='EUR',_adId='00000000-0000-0000-0000-000000000000')

		
		self.GetVersionRequest()
		self.GetStoryModeStatusVersionRequest()
		self.GetPremiumPassStatusRequest()
		self.GetStoryClearCountDayRequest(_page=1)
		self.GetAvailableVipIdListRequest()
		self.GetUserItemAndPointRequest(_page=1)
		self.CheckNewDayRequest()
		self.GetValueRequest(_keys=['game_mode_convert_version'])
		self.GetValueRequest(_keys=['gamemode_unlock'])
		self.GetMissionSetInfoRequest(_page=1)
		self.GetHomeInfoRequest()
		self.GetVersionRequest()
		self.GetPersonalMessageRequest(_checkMessageId=-1,_doNotShowAgain=0)
		self.GetVersionRequest()
		self.GetStoryTopInfoRequest()
		self.ExecuteShopItemGashaRequest(_gashaId=4000100,_platformCode=self._platformId,_romType=self._romType)
		self.getallmail()

	def UserSetting(self,_languageId):
		return Scream.UserSetting(_languageId)

	def Item(self,_categoryId,_itemId,_itemCount):
		return Scream.Item(_categoryId,_itemId,_itemCount)

	def SessionInfo(self,_sessionKey):
		return Scream.SessionInfo(_sessionKey)

	def PartyCharacterEquipmentInfo(self,_characterId,_partyMemberId,_equipmentInsIds):
		return Scream.PartyCharacterEquipmentInfo(_characterId,_partyMemberId,_equipmentInsIds)

	def PartyInfo(self,_partyId,_partyName,_partyCharacters):
		return Scream.PartyInfo(_partyId,_partyName,_partyCharacters)

	def acceptAllMissions(self):
		_missionSetIdList=set()
		page=1
		while(1):
			_missionSetInfoList=self.GetMissionSetInfoRequest(_page=page)['_missionSetInfoList']
			if len(_missionSetInfoList)<=0:	break
			for x in _missionSetInfoList:
				_missionSetIdList.add(x['_missionSetId'])
			page+=1
		page=1
		while(1):
			res=self.GetMissionInfoRequest(_missionSetIdList=list(_missionSetIdList),_page=page)
			if len(res['_missionInfoList'])<=0:	break
			_missionIdList=set()
			for x in res['_missionInfoList']:
				if x['_missionStatus']!=0:
					_missionIdList.add(x['_missionId'])
			self.GetMissionRewardRequest(_missionIdList=list(_missionIdList))
			page+=1

	def rndHex(self,n):
		return ''.join([random.choice('0123456789ABCDEF') for x in range(n)])

	def rndDeviceId(self):
		return '%s-%s-%s-%s-%s'%(self.rndHex(8),self.rndHex(4),self.rndHex(4),self.rndHex(4),self.rndHex(12))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-e','--ecd', help='Where the ecd file is located', required=True)
	parser.add_argument('-r','--region', help='Region gl or jp', required=True)
	parser.add_argument('-d','--device', help='Device iOS or Android', required=True)
	args=parser.parse_args()
	region=args.region.lower()
	if region not in set(['gl','jp']):
		print('wrong region')
		exit(1)
	_romType={'gl':2,'jp':1}[region]
	device=args.device.lower()
	if device not in set(['ios','android']):
		print('wrong device')
		exit(1)
	_platformId={'ios':2,'android':1}[device]
	ecd=parseEcd(args.ecd,_platformId,_romType)
	a=API()
	a.debug=True
	a.setRegion(ecd['region_'])
	a.setLanguage(ecd['loginLanguage_'])
	a.setRom(_romType)
	a.setPlatform(_platformId)
	a.login(ecd['guid_'],ecd['key_'])
	a.doallquests(True)
	a.doallquests(True,True)
	
	a.doallevents(True)
	a.doallevents(True,True)
	a.acceptAllMissions()
