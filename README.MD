code：存放所有源代码
dictionary：字典（勿动）
record：存放用户录音文件  //后续将录音文件处理的中间文件单独放在一个文件夹
        无需将用户录音处理成ds 只需提取音素序列、F0序列
respond：输出的对歌结果
vocal_ds_dataset：存放歌曲ab段的ds文件，已处理的数据集
vocal_part：存放歌曲已经标记拼音但未经ds处理的数据


# 假设
1. 用户只唱上句，用户唱的旋律都在曲库#   v o c a l _ m a t c h  
 #   v o c a l _ m a t c h  
 #   v o c a l _ m a t c h  
 #   v o c a l _ m a t c h  
 #   v o c a l _ m a t c h  
 #   v o c a l _ m a t c h  
 #   v o c a l _ m a t c h  
 #   v o c a l _ m a t c h  
 