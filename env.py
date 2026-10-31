# 基本信息
token       = ""
target      = "" # 群id
target_type = "" # group/user

# 导出信息
raw_dir     = target           # 输出日志目录
output_name = f"{target}.csv"  # 输出消息表文件名

# 爬取速率控制
size        = 50 # 每页爬取多少条
space       = 1  # 爬取等待多少秒
url         = "https://chat-go.jwzhd.com/open-apis/v1/bot/messages"