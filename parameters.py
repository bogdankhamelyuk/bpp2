import os 
import json

class Parameters(object):
    ########################################################################       
    #!!!these values are going to be controlled from slice bar !!!
    _file = open("/home/bogdan/Vs-code-workspace/python/lndf_video/datafile.json","r")
    if os.path.getsize("/home/bogdan/Vs-code-workspace/python/lndf_video/datafile.json") > 0:
        print("is not empty")
        jsonFile = json.load(_file)
        _canny_threshold1     = jsonFile["threshold1"]
        _canny_threshold2     = jsonFile["threshold2"]
        _minLineLength        = jsonFile["minLineLength"]
        _maxLineGap           = jsonFile["maxLineGap"]
        _houghlines_threshold = jsonFile["houghlines_threshold"]
        _camera               = jsonFile["camera"]
    else:
        print("empty")
        _canny_threshold1 = 350 
        _canny_threshold2 = 175
        #!!!these values must be controlled from slice bar
        _minLineLength = 30
        _maxLineGap = 18
        _houghlines_threshold = 25
        _camera = 0
    ######################################################################## 
