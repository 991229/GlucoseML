import nidaqmx
import numpy as np
from nidaqmx import constants
from nidaqmx import stream_readers
from nidaqmx import stream_writers
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.pylab import mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import time,sys
import threading
from statistics import mean
from pandas.core.frame import DataFrame
import joblib
from PIL import ImageTk,Image

pre = joblib .load('./Sunshine.pkl')
#### PPG feature

NUM_CHANNELS = 4
sample_rate = 50                              # Usually sample rate (Hz)
samples_to_acq = 1000                           # How many points do you want to collect
wait_time = samples_to_acq/sample_rate          # Data Acquisition Time in s, very important for the NI task function, and since we have 2048 on both sides, time is 1 s
cont_mode = constants.AcquisitionType.CONTINUOUS              # There is also FINITE for sporadic measurements
iterations = 1
total_wait_time = wait_time * iterations                        

now = datetime.now()
military = now.strftime('%H:%M:%S')     # Just recording the time like 20:32:54 instead of 8:32:54 pm
first_header = ['Some title in here']
second_header = [f'T. Captura: {military}']



##########################################################################################################################################################
##########################################################################################################################################################
########                       NI data detect                         ###################################################################################
##########################################################################################################################################################
##########################################################################################################################################################


# def read_callback(task_handle, every_n_samples_event_type,
#                  number_of_samples, callback_data):

#         #################使用 stream_readers 来提高性能 ##########################
#         # buffer = np.empty((NUM_CHANNELS, number_of_samples), dtype=np.float64,order="C")
#         # read_task.read_many_sample(buffer, number_of_samples, timeout=constants.WAIT_INFINITELY)
#         # data = buffer.T.astype(np.float64)
#         ####################直接使用 read 函数 #############
#         data = task.read(number_of_samples_per_channel=number_of_samples)
#         # non_local_var['All samples'].extend(data)
#         channel1_data.extend(data[0])
#         channel2_data.extend(data[1])
#         channel3_data.extend(data[2])
#         channel4_data.extend(data[3])
#         return 0

    
# with nidaqmx.Task() as task:
#     for i in range(NUM_CHANNELS):
#         task.ai_channels.add_ai_voltage_chan("Dev1/ai{}".format(i),name_to_assign_to_channel="AI{}".format(i),max_val=10,min_val=-10)
#     print("##################################################################")
#     samples_to_acq_new = samples_to_acq * iterations                 # Also multiply by 10 to keep the same ratio, it should be 

#     task.timing.cfg_samp_clk_timing(sample_rate,sample_mode=cont_mode,samps_per_chan=samples_to_acq_new) #一直采，直到停止任务
#     # task.timing.cfg_samp_clk_timing(RATE,sample_mode=constants.AcquisitionType.FINITE,samps_per_chan=300000) #采集指定数量的样本

#     non_local_var = {'All samples': []}
#     channel1_data = []
#     channel2_data = []
#     channel3_data = []
#     channel4_data = []

#     # read_task = stream_readers.AnalogMultiChannelReader(task.in_stream)
#     # write_task = stream_writers.AnalogMultiChannelWriter(task.out_stream)

#     task.register_every_n_samples_acquired_into_buffer_event(
#         samples_to_acq, read_callback)  # samples_to_acq is the number_of_samples (parameter) of read_callback (function)

#     task.start()
#     startTime = time.time()
#     while True:
#         if len(channel1_data)>=500:
#             break
#     print("耗费时间:",time.time()-startTime)
#     task.stop()

#     print("数据总量:",len(channel1_data))
#     # print(channel1_data)


# plt.plot(x,channel1_data)
# plt.show()

##########################################################################################################################################################
##########################################################################################################################################################
########                       Tkinter UI interface                        ###############################################################################
##########################################################################################################################################################
##########################################################################################################################################################

from tkinter import *
import hashlib
import time
from ttkbootstrap import Style
style = Style()
style = Style(theme='sandstone')
# ['vista', 'classic', 'cyborg', 'journal', 'darkly', 'flatly', 'clam', 'alt', 'solar', 'minty', 'litera', 'united', 'xpnative', 'pulse', 'cosmo', 'lumen', 'yeti', 'superhero', 'winnative', 'sandstone', 'default']
TOP6 = style.master


mpl.rcParams['axes.unicode_minus'] = False  # 负号显示

global init_window
global PPGGraphLabel, PPGData, runFlag
global BloodGlucosePredictValue, heartRate
runFlag = True
PPGData = []
o_glucose = []
y_glucose = [8.1]
r_glucose = [3.9]
g_glucose = [4.4, 5.6, 4.5, 5.1, 4.9, 6.4, 6.3, 7.1, 6.9]
BloodGlucosePredictValue = 0
heartRate = 0
systolic_peak_value = 0
'''
图表类，定义时参数root为父控件
'''
class PPGGraph():
    def __init__(self, root):
        self.root = root  # 主窗体
        self.canvas = tk.Canvas()  # create a canvas to imshow the fig of plt
        self.figure = self.create_matplotlib()  # return the fig of plt
        self.showGraphIn(self.figure)  # show the fig of plt


    '''generate fig'''
    def create_matplotlib(self):
        # 创建绘图对象f
        f = plt.figure(num=2, figsize=(6, 4), dpi=100, edgecolor='green', frameon=True)
        # 创建一副子图
        self.fig11 = plt.subplot(1, 1, 1)
        self.line11, = self.fig11.plot([], [])
        self.BG_text = self.fig11.text(x=0.02, y=0.98, s='Blood sugar: --', fontsize=20,
                                   transform=self.fig11.transAxes, verticalalignment='top')
        # self.HR_text = self.fig11.text(x=0.02, y=0.86, s='Heart rate: --', fontsize=20,
        #                            transform=self.fig11.transAxes, verticalalignment='top')
        def setLabel(fig, title, titleColor="red"):
            fig.set_title("Blood glucose PPG waveform of "+title, color=titleColor)  # 设置标题
            fig.set_xlabel('Time (s)') 
            fig.set_ylabel("Current (μ A)") 
        setLabel(self.fig11, "ZYJ")
        # fig1.set_yticks([-1, -1 / 2, 0, 1 / 2, 1])  # 设置坐标轴刻度
        f.tight_layout() # 自动紧凑布局
        return f

    '''show the fig into tkinter'''
    def showGraphIn(self, figure):
        self.canvas = FigureCanvasTkAgg(figure, self.root)
        self.canvas.draw()  
        self.canvas.get_tk_widget().pack(side=tk.TOP) #, fill=tk.BOTH, expand=1

        # # 把matplotlib绘制图形的导航工具栏显示到tkinter窗口上
        # toolbar = NavigationToolbar2Tk(self.canvas,
        #                                self.root)  
        # toolbar.update()
        # self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    '''update the fig to make it dynamic'''
    def updatePPGGraph(self, PPGPointData, BG, HR, s_value):
        x = [i*0.02 for i in range(len(PPGPointData))]
        self.line11.set_xdata(x) # x轴也必须更新
        self.line11.set_ydata(PPGPointData)  # 更新y轴数据
        #  更新x数据，但未更新绘图范围。当我把新数据放在绘图上时，它完全超出了范围。解决办法是增加：
        self.fig11.relim()
        self.fig11.autoscale_view()
        if max(x) > 4:
            self.fig11.set_xlim(max(x)-4, max(x))
            self.fig11.set_ylim(PPGPointData[len(PPGPointData)-200]-0.2, max(PPGPointData)+0.2)
        plt.draw()
        # self.canvas.draw_idle()

        self.BG_text.set_text(f'Blood sugar: %s mmol/L' % round(BG, 2) if BG != 0 else 'Blood sugar: --')
        # self.HR_text.set_text('Heart rate: %s ' % round(HR, 1) if HR !=0 else 'Heart rate: --')
        
'''
更新数据，在次线程中运行
'''

channel = [1.426977754861582, 1.3742223476874642, 1.3642502890143078, 1.3626418924541213, 1.3626418924541213, 1.3668237235106062, 1.3716489131911658, 1.3742223476874642, 1.3806559339282103, 1.3861244822328445, 1.388697916729143, 1.3925580684735905, 1.3964182202180382, 1.4018867685226724, 1.4060685995791573, 1.4044602030189708, 1.4096070720115677, 1.4128238651319407, 1.4170056961884256, 1.4199008099967614, 1.417327375500463, 1.3938447857217398, 1.3587817407096736, 1.3407676992355846, 1.3301522819383536, 1.3275788474420551, 1.3272571681300178, 1.3311173198744655, 1.33176067849854, 1.3388376233633608, 1.3439844923559576, 1.3494530406605918, 1.3568516648374498, 1.3603901372698601, 1.3648936476383824, 1.359103420021711, 1.3542782303411514, 1.3542782303411514, 1.3510614372207783, 1.3545999096531887, 1.3616768545180093, 1.3674670821346808, 1.3755090649356134, 1.380334254616173, 1.3861244822328445, 1.3944881443458144, 1.3996350133384112, 1.300921735865604, 1.4079986754513811, 1.4118588271958288, 1.4144322616921272, 1.4147539410041645, 1.4199008099967614, 1.4231176031171344, 1.4276211134856567, 1.4314812652301043, 1.43437637903844, 1.435341416974552, 1.4282644721097313, 1.3989916547143366, 1.3636069303902332, 1.343341133731883, 1.3388376233633608, 1.3356208302429877, 1.339159302675398, 1.3398026612994727, 1.3436628130439203, 1.3468796061642934, 1.3536348717170767, 1.3555649475893006, 1.359103420021711, 1.3610334958939347, 1.3600684579578228, 1.3626418924541213, 1.3600684579578228, 1.3542782303411514, 1.3552432682772633, 1.3574950234615244, 1.364571968326345, 1.3652153269504197, 1.3703621959430166, 1.380334254616173, 1.383551047736546, 1.390949671913404, 1.39738325815415, 1.404781882331008, 1.4070336375152692, 1.4128238651319407, 1.4150756203162018, 1.4182924134365749, 1.4231176031171344, 1.427942792797694, 1.4318029445421416, 1.435341416974552, 1.4398449273430742, 1.437593172158813, 1.424725999677321, 1.3854811236087698, 1.3594250993337482, 1.346557926852256, 1.3381942647392862, 1.342376095795771, 1.34012434061151, 1.3417327371716965, 1.3452712096041068, 1.347522964788368, 1.3542782303411514, 1.3600684579578228, 1.3629635717661586, 1.3648936476383824, 1.3610334958939347, 1.3562083062133752, 1.3491313613485545, 1.3481663234124426, 1.3533131924050394, 1.359103420021711, 1.364571968326345, 1.3703621959430166, 1.3838727270485833, 1.3896629546652548, 1.3977049374661874, 1.300278375624858, 1.4044602030189708, 1.4105721099476796, 1.41411058238009, 1.4179707341245376, 1.4240826410532463, 1.4301945479819551, 1.4324463031662162, 1.437593172158813, 1.4414533239032608, 1.4408099652791861, 1.426977754861582, 1.3938447857217398, 1.3658586855744943, 1.3491313613485545, 1.3491313613485545, 1.3472012854763307, 1.3484880027244799, 1.3529915130930021, 1.3562083062133752, 1.3648936476383824, 1.3684321200707927, 1.3780824994319119, 1.3825860098004341, 1.379369216680061, 1.3771174614958, 1.3745440269995015, 1.3681104407587554, 1.3703621959430166, 1.3706838752550539, 1.372935630439315, 1.3777608201198746, 1.383551047736546, 1.3925580684735905, 1.3986699754022993, 1.40574692026712, 1.4112154685717542, 1.4128238651319407, 1.4166840168763883, 1.421509206556948, 1.428907830733806, 1.4305162272939924, 1.4356630962865893, 1.4398449273430742, 1.4440267583995592, 1.4337330204143655, 1.4022084478347097, 1.3767957821837626, 1.3603901372698601, 1.351704795844853, 1.3526698337809648, 1.3552432682772633, 1.3562083062133752, 1.3603901372698601, 1.3658586855744943, 1.3668237235106062, 1.3751873856235761, 1.3809776132402476, 1.3848377649846952, 1.3838727270485833, 1.3774391408078372, 1.3732573097513523, 1.3722922718152404, 1.3722922718152404, 1.3771174614958, 1.3822643304883968, 1.384516085672658, 1.3922363891615532, 1.3977049374661874, 1.4031734857708216, 1.409928751323605, 1.4118588271958288, 1.417327375500463, 1.420544168620836, 1.424725999677321, 1.4282644721097313, 1.43437637903844, 1.4388798894069623, 1.438558210094925, 1.43437637903844, 1.4118588271958288, 1.3780824994319119, 1.358138382085599, 1.3488096820365172, 1.3452712096041068, 1.3459145682281815, 1.3488096820365172, 1.3494530406605918, 1.3520264751568902, 1.3578167027735617, 1.362320213142084, 1.364571968326345, 1.3690754786948673, 1.3681104407587554, 1.366502044198569, 1.3597467786457855, 1.3594250993337482, 1.3603901372698601, 1.359103420021711, 1.3668237235106062, 1.3706838752550539, 1.3713272338791285, 1.3777608201198746, 1.384516085672658, 1.3858028029208072, 1.3915930305374786, 1.3948098236578517, 1.39738325815415, 1.4041385237069335, 1.4031734857708216, 1.40574692026712, 1.4115371478837915, 1.41411058238009, 1.4176490548125003, 1.4176490548125003, 1.4038168443948962, 1.3755090649356134, 1.3587817407096736, 1.3478446441004053, 1.3436628130439203, 1.341089378547622, 1.3446278509800322, 1.3472012854763307, 1.3494530406605918, 1.3523481544689275, 1.3510614372207783, 1.3552432682772633, 1.3642502890143078, 1.365537006262457, 1.362320213142084, 1.361355175205972, 1.3565299855254125, 1.3555649475893006, 1.3600684579578228, 1.3619985338300467, 1.361355175205972, 1.365537006262457, 1.3710055545670912, 1.3780824994319119, 1.3822643304883968, 1.3851594442967325, 1.390949671913404, 1.3948098236578517, 1.3964182202180382, 1.3986699754022993, 1.300600055745231, 1.4051035616430454, 1.4076769961393438, 1.409928751323605, 1.413145544443978, 1.4153972996282391, 1.4166840168763883, 1.401565089210635, 1.3767957821837626, 1.3568516648374498, 1.3462362475402188, 1.3439844923559576, 1.3452712096041068, 1.3455928889161441, 1.3491313613485545, 1.3510614372207783, 1.3523481544689275, 1.3594250993337482, 1.359103420021711, 1.3642502890143078, 1.364571968326345, 1.3616768545180093, 1.3616768545180093, 1.3600684579578228, 1.3603901372698601, 1.3639286097022705, 1.3648936476383824, 1.3693971580069046, 1.3716489131911658, 1.3771174614958, 1.3806559339282103, 1.3851594442967325, 1.3906279926013667, 1.3957748615939636, 1.399313334026374, 1.4012434098985977, 1.4054252409550827, 1.409928751323605, 1.4115371478837915, 1.4112154685717542, 1.4160406582523137, 1.4179707341245376, 1.4221525651810225, 1.4092853926995303, 1.3912713512254413, 1.3690754786948673, 1.3600684579578228, 1.3529915130930021, 1.349774719972629, 1.3536348717170767, 1.3552432682772633, 1.3545999096531887, 1.3565299855254125, 1.365537006262457, 1.369718837318942, 1.3764741028717253, 1.3751873856235761, 1.3755090649356134, 1.3732573097513523, 1.3748657063115388, 1.3722922718152404, 1.372935630439315, 1.379369216680061, 1.381299292552285, 1.3851594442967325, 1.389984633977292, 1.390949671913404, 1.398348296090262, 1.300921735865604, 1.4038168443948962, 1.4073553168273065, 1.41411058238009, 1.4166840168763883, 1.4166840168763883, 1.417327375500463, 1.423760961741209, 1.424725999677321, 1.4301945479819551, 1.4350197376625147, 1.4369498135347385, 1.4392015687189996, 1.428907830733806, 1.300278375624858, 1.381299292552285, 1.36875379938283, 1.3610334958939347, 1.3597467786457855, 1.3578167027735617, 1.361355175205972, 1.3607118165818974, 1.361355175205972, 1.3658586855744943, 1.3713272338791285, 1.3742223476874642, 1.3735789890633896, 1.3710055545670912, 1.3706838752550539, 1.3668237235106062, 1.369718837318942, 1.3735789890633896, 1.3767957821837626, 1.3774391408078372, 1.3854811236087698, 1.388697916729143, 1.3925580684735905, 1.3986699754022993, 1.4028518064587843, 1.406711958203232, 1.412180506507866, 1.4115371478837915, 1.416362337564351, 1.4147539410041645, 1.417327375500463, 1.4211875272449106, 1.4250476789893582, 1.4301945479819551, 1.4324463031662162, 1.4359847755986266, 1.4401666066551115, 1.4430617204634473, 1.4324463031662162, 1.40574692026712, 1.381299292552285, 1.3681104407587554, 1.3597467786457855, 1.3574950234615244, 1.3584600613976363, 1.3607118165818974, 1.3629635717661586, 1.3619985338300467, 1.3668237235106062, 1.3710055545670912, 1.373900668375427, 1.3735789890633896, 1.3735789890633896, 1.372935630439315, 1.3710055545670912, 1.3671454028226435, 1.3713272338791285, 1.371970592503203, 1.3758307442476507, 1.3784041787439492, 1.386767840856919, 1.3896629546652548, 1.3977049374661874, 1.3980266167782247, 1.300278375624858, 1.402530127146747, 1.4060685995791573, 1.409928751323605, 1.4112154685717542, 1.4160406582523137, 1.4186140927486122, 1.4221525651810225, 1.420544168620836, 1.4256910376134329, 1.4301945479819551, 1.4327679824782535, 1.4369498135347385, 1.4424183618393727, 1.4346980583504774, 1.4134672237560153, 1.3816209718643222, 1.3642502890143078, 1.3607118165818974, 1.3565299855254125, 1.3568516648374498, 1.3619985338300467, 1.3642502890143078, 1.3703621959430166, 1.372935630439315, 1.379369216680061, 1.381299292552285, 1.3870895201689564, 1.3861244822328445, 1.3832293684245087, 1.3796908959920984, 1.3777608201198746, 1.3816209718643222, 1.3829076891124714, 1.3874111994809937, 1.3954531822819263, 1.3977049374661874, 1.4060685995791573, 1.40574692026712, 1.4134672237560153, 1.4170056961884256, 1.423760961741209, 1.4253693583013956, 1.4292295100458432, 1.4308379066060297, 1.4363064549106639, 1.4379148514708504, 1.4424183618393727, 1.4466001928958576, 1.4504603446403053, 1.4556072136329021, 1.4591456860653125, 1.4507820239523426, 1.4199008099967614, 1.3948098236578517, 1.380334254616173, 1.3716489131911658, 1.3735789890633896, 1.3774391408078372, 1.3748657063115388, 1.3806559339282103, 1.384516085672658, 1.3903063132893294, 1.3957748615939636, 1.300921735865604, 1.4038168443948962, 1.4041385237069335, 1.4044602030189708, 1.3980266167782247, 1.300278375624858, 1.300600055745231, 1.4012434098985977, 1.4063902788911946, 1.409928751323605, 1.4192574513726868, 1.4250476789893582, 1.4292295100458432, 1.4318029445421416, 1.4411316445912234, 1.4433833997754846, 1.450138665328268, 1.4517470618884545, 1.4546421756967902, 1.4572156101930887, 1.4578589688171633, 1.461719120561611, 1.4655792723060586, 1.4704044619866181]

def updataData():
    global PPGData,runFlag,BloodGlucosePredictValue,heartRate,systolic_peak_value
    i = 0
    systolic_peak = []
    systolic_peak_ratio = []
    diastolic_peak = []
    diastolic_peak_ratio = []
    dicrotic_notch= []
    dicrotic_notch_ratio = []
    bottom = []
    cofficient_rise = []
    cofficient_decline = []
    pulse_width = []
    DEIT = []
    dicrotic_notch_row = 0
    bottom_row = 0
    bottom_value = 0
    systolic_peak_row = 0
    diastolic_peak_row = 0
    while runFlag:
        PPGData.append(channel[i])
        # PPGData.append(channel[i]/100000)
        if i >= 400:
                # systolic_peak
            if PPGData[i-15] > PPGData[i-15-10] and PPGData[i-15] > PPGData[i-15+10] and PPGData[i-15] > PPGData[i-15+1] and PPGData[i-15] > PPGData[i-15-1]:
                systolic_peak_row = i-15
                systolic_peak_value = PPGData[i-15]  # 收缩峰 = 峰值 - 底部值   -----------
                if bottom_row != 0 and 15 < (systolic_peak_row - bottom_row) < 30:
                    #print("i-15:", systolic_peak_row, " ", bottom_row-systolic_peak_row, " ", "s_peak_value:", PPGData[i-15]-bottom_value, "Peak:", PPGData[i-15], "bottom:", bottom_value)
                    systolic_peak.append(PPGData[i-15] - bottom_value)
                    systolic_peak_ratio.append((PPGData[i-15] - bottom_value)/bottom_value)
                    cofficient_rise.append((systolic_peak_value-bottom_value)/(systolic_peak_row-bottom_row)) # 上升斜率 = (收缩峰 - 最低点)/（收缩峰时间 - 最低点时间）
                if diastolic_peak_row != 0: #and diastolic_peak_row - systolic_peak_row :
                    DEIT.append(systolic_peak_row - diastolic_peak_row)  # DEIT = 收缩峰到舒张峰的时长
                #print("sys_row:", systolic_peak_row)
                #print("bottom_row:", bottom_row)
                
            # dicrotic_notc
            if PPGData[i-15] < PPGData[i-15-4] and PPGData[i-15] < PPGData[i-15+4] and PPGData[i-15] > PPGData[i-15-10]:
                if bottom_row != 0 and  7 < (i-15 - bottom_row) < 25:
                    dicrotic_notch.append(PPGData[i-15] - bottom_value)
                    #print("i-15:", i-15, " ", bottom_row-i-15, " ", "d_notc:", PPGData[i-15]-bottom_value)
                    dicrotic_notch_ratio.append((PPGData[i-15] - bottom_value)/bottom_value)
                
            # diastolic_peak
            if PPGData[i-15] > PPGData[i-15-10] and PPGData[i-15] > PPGData[i-15+3] and PPGData[i-15] < PPGData[i-15+13] and PPGData[i-15] > PPGData[i-15+2] and PPGData[i-15] > PPGData[i-15-2]:
                if bottom_row != 0 and 3 < (i-15 - bottom_row) < 35:
                    diastolic_peak.append(PPGData[i-15] - bottom_value)
                    diastolic_peak_ratio.append((PPGData[i-15] - bottom_value)/bottom_value)
                    #print("i-15:", i-15, " ", bottom_row-i-15, " ", "d_peak:", PPGData[i-15]-bottom_value)
                diastolic_peak_row = i-15

            #bottom
            if PPGData[i-15] < PPGData[i-15-15] and PPGData[i-15] < PPGData[i-15+15] and PPGData[i-15] < PPGData[i-15+1] and PPGData[i-15] < PPGData[i-15-1] and PPGData[i-15] < PPGData[i-15+3] and PPGData[i-15] < PPGData[i-15-3] and PPGData[i-15] < PPGData[i-15+2] and PPGData[i-15] < PPGData[i-15-2]:
                bottom.append(PPGData[i-15])
                #print("i-15:", i-15, " ", bottom_row-i-15, " ", "d_peak:", PPGData[i-15])
                if bottom_row != 0 and 15 < i-15-bottom_row < 55:
                    pulse_width.append((i-15 - bottom_row))  # 脉冲宽度 = 两最低点时长差
                    heartRate = 60/((i-15 - bottom_row)*0.02)
                print("pulse_width: ", i-15-bottom_row, "bottomrow:", i-15)
                bottom_row = i-15
                bottom_value = PPGData[i-15]
                if systolic_peak_row != 0 and 5 < (bottom_row-systolic_peak_row) < 15:
                    cofficient_decline.append((bottom_value-systolic_peak_value)/(bottom_row-systolic_peak_row)) # 下降斜率 = （最低点 - 收缩峰）/ （最低点时间 - 收缩峰时间）


            if (len(PPGData) % 50 == 0) and (len(PPGData) > 600):
                systolic_peak_value_mean = mean(systolic_peak)*1E-5
                diastolic_peak_value_mean = mean(diastolic_peak)*1E-5
                dicrotic_notch_value_mean = mean(dicrotic_notch)*1E-5
                bottom_value_mean = mean(bottom)*1E-5
                cofficient_decline_value = mean(cofficient_decline)*1E-5
                cofficient_rise_value = mean(cofficient_rise)*1E-5
                pulse_width_value = mean(pulse_width)
                DEIT_value = mean(DEIT)
                featureTrain = [systolic_peak_value_mean, (-1)*mean(systolic_peak_ratio), diastolic_peak_value_mean, (-1)*mean(diastolic_peak_ratio), dicrotic_notch_value_mean, (-1)*mean(dicrotic_notch_ratio), (-1)*bottom_value_mean, cofficient_decline_value, cofficient_rise_value, pulse_width_value, DEIT_value]
                
                # predict
                # featureTrain: (1, 11)
                featureTrain = DataFrame(featureTrain)
                featureTrain = featureTrain.T 
                # print(featureTrain)  
                BloodGlucosePredictValue = round(pre.predict(featureTrain)[0], 2)  #使用predict预测 
                
        time.sleep(0.02)
        i = i+1
'''
更新窗口
'''
def updateWindow():
    global init_window
    global PPGGraphLabel, PPGData, runFlag, BloodGlucosePredictValue,heartRate,systolic_peak_value
    if runFlag:
        PPGGraphLabel.updatePPGGraph(PPGData, BloodGlucosePredictValue, heartRate, systolic_peak_value)
    init_window.after(20, updateWindow)  # 20ms更新画布
'''
关闭窗口触发函数，关闭S7连接，置位flag
'''
def closeWindow():
    global runFlag
    runFlag = False
    sys.exit()
'''
创建控件
'''
from PIL import ImageTk, Image

# 在函数外部创建图像对象
image_path = './JNU.png'
im = None

def GUI_Start():
    global init_window
    init_window = tk.Tk()
    # init_windowX, init_windowY = int((displayWidth - init_windowWidth) /
    #                  2), int((displayHeight - init_windowHeight - 70) / 2)
    init_window.title("BG software")
    """ 
    Left Top
    """
    graphFrame = tk.Frame(init_window, width=70, height=20) # 创建图表控件
    graphFrame.grid(row=1, column=0, rowspan=10, columnspan=10)
    global PPGGraphLabel
    PPGGraphLabel = PPGGraph(graphFrame)

    recv_data = threading.Thread(target=updataData)  # 开启线程
    recv_data.start()

    updateWindow()  # 更新画布    

    """ 
    Right Top
    """
    RightTopCanvas = tk.Canvas(init_window, width=600, height=300)                                                                                                         
    RightTopCanvas.config(bg='black')
    RightTopCanvas.grid(row=0, column=10, rowspan=12, columnspan=10)
    # f = plt.figure(num=2, figsize=(6, 4), dpi=100, edgecolor='green', frameon=True)
    #     # 创建一副子图
    # self.fig11 = plt.subplot(1, 1, 1)
    # self.line11, = self.fig11.plot([], [])
    # self.canvas = FigureCanvasTkAgg(figure, self.root)
    # self.canvas.draw()  
    # self.canvas.get_tk_widget().pack(side=tk.TOP) #, fill=tk.BOTH, expand=1
    f = plt.figure(figsize=(5, 4.2))
    plt.xlabel('Blood glucose (mmol L-1)')
    plt.title("Blood glucose statistics")
    plt.ylabel('Count')
    plt.xlim(0, 20)
    b = list(range(0, 20, 1))
    plt.hist((o_glucose, y_glucose, g_glucose, r_glucose), bins=b, histtype='stepfilled', color=["SandyBrown", "Khaki", "LawnGreen", "DarkSalmon"]) #, orientation='horizontal'
    RightTopFig = FigureCanvasTkAgg(f, RightTopCanvas)
    RightTopFig.draw()
    RightTopFig.get_tk_widget().pack(side=tk.TOP)
    
    """ 
    Left Bottom
    """
    Title1OfLeftBottom = tk.Label(init_window, text='Glucose Pattern Insights', font=('Arial', 14, 'bold'),width=40, height=1, anchor='w')
    Title1OfLeftBottom.config(fg='DeepSkyBlue')
    Title1OfLeftBottom.grid(row=12, column=0, columnspan=10)
    Title2OfLeftBottom = tk.Label(init_window, text='Selected dates: 6 Jan - 12 Jan 2024 (7 Days)', font=('Arial', 12, 'bold'), width=50, height=1, anchor='w')
    Title2OfLeftBottom.config(bg='Gainsboro')
    Title2OfLeftBottom.grid(row=13, column=0, columnspan=10)
    Title3OfLeftBottom = tk.Label(init_window, text='Time in Ranges', font=('Arial', 12, 'bold'), width=50, height=1, anchor='w')
    Title3OfLeftBottom.config(bg='Gainsboro')
    Title3OfLeftBottom.grid(row=14, column=0, columnspan=10)
    
    piePicCanvas = tk.Canvas(init_window, width=500, height=300)
    # piePicCanvas.config(bg='black')
    piePicCanvas.grid(row=15, column=0, rowspan=8, columnspan=10)
    piePicCanvas.create_arc(270,280,20,30,start=0,extent=10,fill="SandyBrown",width=4,outline='white')
    piePicCanvas.create_arc(270,280,20,30,start=10,extent=20,fill="Khaki",width=4,outline='white')
    piePicCanvas.create_arc(270,280,20,30,start=30,extent=310,fill="LawnGreen",width=4,outline='white')
    piePicCanvas.create_arc(270,280,20,30,start=340,extent=20,fill="DarkSalmon",width=4,outline='white')
    
    piePicCanvas.create_line(260, 145, 500, 145, fill='Gainsboro', width=3)
    piePicCanvas.create_line(255, 117, 500, 117, fill='Gainsboro', width=3)
    piePicCanvas.create_line(225, 70, 500, 70, fill='Gainsboro', width=3)
    piePicCanvas.create_line(255, 180, 500, 180, fill='Gainsboro',width=3)
    
    piePicCanvas.create_text(320, 135, text= "Very High",fill="SandyBrown",font=('Helvetica 12 bold'))
    piePicCanvas.create_text(400, 135, text= "> 10.1 mmol/L", fill='black', font=("Arial 8"))
    piePicCanvas.create_text(480, 135, text="{} %".format(HeightOfColorBarOrange*10), fill='black', font=("Arial 12 bold"))
    
    piePicCanvas.create_text(300, 107, text= "High",fill="Khaki",font=('Helvetica 12 bold'))
    piePicCanvas.create_text(380, 107, text= "8.1 to 10.1 mmol/L", fill='black', font=("Arial 8"))
    piePicCanvas.create_text(460, 107, text="{} %".format(HeightOfColorBarYellow*10), fill='black', font=("Arial 12 bold"))
    
    piePicCanvas.create_text(270, 60, text= "Target",fill="LawnGreen",font=('Helvetica 12 bold'))
    piePicCanvas.create_text(350, 60, text= "4.0 to 8.0 mmol/L", fill='black', font=("Arial 8"))
    piePicCanvas.create_text(430, 60, text="{} %".format(HeightOfColorBarGreen*10), fill='black', font=("Arial 12 bold"))
    
    piePicCanvas.create_text(300, 170, text= "Low",fill="DarkSalmon",font=('Helvetica 12 bold'))
    piePicCanvas.create_text(380, 170, text= "4.0 < mmol/L", fill='black', font=("Arial 8"))
    piePicCanvas.create_text(460, 170, text="{} %".format(HeightOfColorBarRed*10), fill='black', font=("Arial 12 bold"))

    """ 
    Right Bottom
    """
    RightBottomCanvas = tk.Canvas(init_window, width=450, height=200, bd=1, relief='raised')                                                                                                         
    # RightBottomCanvas.config(bg='black')
    RightBottomCanvas.grid(row=13, column=11, rowspan=10, columnspan=7)
    RightBottomCanvas.create_text(100, 15, text='Glucose Statistics', fill='DeepSkyBlue', font=('Arial', 14, 'bold'))
    RightBottomCanvas.create_text(80, 55, text='Average Glucose:', fill='Black', font=('Arial', 12))
    RightBottomCanvas.create_line(25, 70, 300, 70, fill='Gainsboro')
    RightBottomCanvas.create_text(250, 55, text = "{} mmol L-1".format(averageGlucose), fill='Black', font=('Arial', 14, 'bold'))
    RightBottomCanvas.create_text(75, 105, text='Highest Glucose', fill='Black', font=('Arial', 12))
    RightBottomCanvas.create_line(25, 120, 300, 120, fill='Gainsboro')
    RightBottomCanvas.create_text(250, 105, text = "{} mmol L-1".format(maxGlucose), fill='Black', font=('Arial', 14, 'bold'))
    RightBottomCanvas.create_text(75, 155, text='Lowest Glucose', fill='Black', font=('Arial', 12))
    RightBottomCanvas.create_line(25, 170, 300, 170, fill='Gainsboro')
    RightBottomCanvas.create_text(250, 155, text = "{} mmol L-1".format(minGlucose), fill='Black', font=('Arial', 14, 'bold'))
    
    init_window.mainloop()

if __name__ == '__main__':
    lenVeryHigh = len(o_glucose)
    lenHigh = len(y_glucose)
    lenTarget = len(g_glucose)
    lenLow = len(r_glucose)
    lenALL = lenVeryHigh+lenHigh+lenLow+lenTarget
    
    HeightOfColorBarOrange = round((lenVeryHigh/lenALL)*10, 1)
    HeightOfColorBarYellow = round((lenHigh/lenALL)*10, 1)
    HeightOfColorBarGreen = round((lenTarget/lenALL)*10, 1)
    HeightOfColorBarRed = round((lenLow/lenALL)*10, 1)
    
    eachMeanGlucoseList = [mean(o_glucose) if o_glucose else 0, mean(y_glucose) if y_glucose else 0, mean(g_glucose) if g_glucose else 0, mean(r_glucose) if r_glucose else 0]
    averageGlucose = round(mean([num for num in eachMeanGlucoseList if num != 0]), 1)
    maxGlucose = max(o_glucose) if o_glucose else max(y_glucose)
    minGlucose = min(r_glucose)
    GUI_Start()


# _tkinter.TclError: image "pyimage21" doesn't exist





















