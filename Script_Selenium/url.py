# Argument
dut_url = "http://192.168.50.1/"
# 網路設定精靈
qis_url = dut_url + "QIS_wizard.htm"

index_url = dut_url+"index.asp"

# Lan
adv_dhcp_url = dut_url + "Advanced_DHCP_Content.asp"

# Wan 廣域網路
adv_wan_url = dut_url+ "Advanced_WAN_Content.asp"
adv_wan_port_url =  dut_url+ "Advanced_WANPort_Content.asp"
adv_wan_trigger = dut_url + "Advanced_WANPort_Content.asp"
adv_wan_virtual = dut_url + "Advanced_VirtualServer_Content.asp"
adv_wan_exposed = dut_url + "Advanced_Exposed_Content.asp"
adv_wan_ddns = dut_url + "Advanced_ASUSDDNS_Content.asp"
adv_wan_natpass = dut_url + "Advanced_NATPassThrough_Content.asp"
adv_sys_url =  dut_url+ "Advanced_System_Content.asp"


adv_fw_url =  dut_url+ "Advanced_FirmwareUpgrade_Content.asp"
adv_fw_url =  dut_url+ "Advanced_FirmwareUpgrade_Content.asp"


analysis_url =  dut_url+ "Main_Analysis_Content.asp"
aimesh_url = dut_url+"AiMesh.asp"
aiportection_url =  dut_url + "AiProtection_HomeProtection.asp"
# 家長電腦控制程式
aiportection_web_url = dut_url +"AiProtection_WebProtector.asp"

cloud_url = dut_url + "cloud_main.asp"
guest_url = dut_url+ "Guest_network.asp"

reset_default_url =  dut_url+ "Advanced_SettingBackup_Content.asp"
disable_redirect_url =  dut_url+ "Main_Login.asp?redirect=false"

# Adaptive Qos
qos_url =dut_url+ "QoS_EZQoS.asp"
qos_webhistory_url = dut_url+ "AdaptiveQoS_WebHistory.asp"

# USB相關應用
usb_url = dut_url + "APP_Installation.asp"

# aicloud
aicloud_url = dut_url + "cloud_main.asp"

# 無線網路
# 定義各相對路徑
base_url = dut_url
relative_paths = [
    "Advanced_Wireless_Content.asp",
    "Advanced_WWPS_Content.asp",
    "Advanced_WMode_Content.asp",
    "Advanced_ACL_Content.asp",
    "Advanced_WSecurity_Content.asp",
    "Advanced_WAdvanced_Content.asp",
    "Advanced_Roaming_Block_Content.asp"
]
# 使用列表生成式來生成完整的 URL
wireless_urls = [base_url + path for path in relative_paths]
# wireless_urls = [
#     dut_url + "Advanced_Wireless_Content.asp",
#     dut_url + "Advanced_WWPS_Content.asp",
#     dut_url + "Advanced_WMode_Content.asp",
#     dut_url + "Advanced_ACL_Content.asp",
#     dut_url + "Advanced_WSecurity_Content.asp",
#     dut_url + "Advanced_WAdvanced_Content.asp",
#     dut_url + "Advanced_Roaming_Block_Content.asp"
# ]

# 區域網路
lan_urls = [
    dut_url + "Advanced_LAN_Content.asp",
    dut_url + "Advanced_DHCP_Content.asp",
    dut_url + "Advanced_GWStaticRoute_Content.asp",
    dut_url + "Advanced_IPTV_Content.asp",
    dut_url + "Advanced_SwitchCtrl_Content.asp"
]

# 廣域網路
adv_wan_url

# VPN
vpn_url = dut_url + "Advanced_VPNServer_Content.asp"

# 防火牆
firewall_urls = [
    dut_url + "Advanced_BasicFirewall_Content.asp",
    dut_url + "Advanced_URLFilter_Content.asp",
    dut_url + "Advanced_KeywordFilter_Content.asp",
    dut_url + "Advanced_Firewall_Content.asp"
]

# 系統管理
administration_urls = [
    dut_url + "Advanced_OperationMode_Content.asp",
    dut_url + "Advanced_System_Content.asp",
    dut_url + "Advanced_FirmwareUpgrade_Content.asp",
    dut_url + "Advanced_SettingBackup_Content.asp",
    dut_url + "Advanced_Feedback.asp",
    dut_url + "Advanced_Privacy.asp"
]

# System Log
system_log_urls = [
    dut_url + "Main_LogStatus_Content.asp",
    dut_url + "Main_WStatus_Content.asp",
    dut_url + "Main_DHCPStatus_Content.asp",
    dut_url + "Main_IPV6Status_Content.asp",
    dut_url + "Main_RouteStatus_Content.asp",
    dut_url + "Main_IPTStatus_Content.asp",
    dut_url + "Main_ConnStatus_Content.asp"
]

# Network Tools
net_tool_urls = [
    dut_url + "Main_Analysis_Content.asp",
    dut_url + "Main_Netstat_Content.asp",
    dut_url + "Main_WOL_Content.asp",
    dut_url + "Advanced_Smart_Connect.asp"
]
# network_analysis_url = dut_url + "Main_Analysis_Content.asp"
# netstat_url = dut_url + "Main_Netstat_Content.asp"
# wakeonlan_url = dut_url + "Main_WOL_Content.asp"
# smart_connect_url = dut_url + "Advanced_Smart_Connect.asp"