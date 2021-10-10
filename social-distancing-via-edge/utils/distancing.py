import cv2
import itertools
import numpy as np
from utils.distancing_class import Configs, Person, IdTable
from scipy.spatial import ConvexHull

def calculate_box(box):
    pLeft, pTop, pRight, pBot = box
    height = int(pBot - pTop)
    coord  = (int(pLeft + pRight) //2, int(pBot))  # bottom
    return height, coord

def is_valid(idTable, person1, person2):
    validHeights = abs(person1.get_height() - person2.get_height()) < 30 ## need to be fixed
    
    diffThres  = person1.get_height() + person2.get_height()
    validDistance = abs(person1.get_coord()[0] - person2.get_coord()[0]) < diffThres and \
                    abs(person1.get_coord()[1] - person2.get_coord()[1]) < diffThres

    parentId1 = idTable.find_parentId(person1.get_id())
    parentId2 = idTable.find_parentId(person2.get_id())
    validParents = parentId1 != parentId2

    return validHeights and validDistance and validParents

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return ((x2 - x1)**2 + (y2 - y1)**2) **0.5

def calculate_distance_threshold(height1, height2):
    pixelRatio = (height1 + height2) / (170 + 170)
    distHighRisk = 150 * pixelRatio     # 1.5 meter
    distLowRisk  = 250 * pixelRatio     # 2.5 meter
    return distHighRisk, distLowRisk

def create_idx_combination(peopleList):
    peopleIdx = list(range(len(peopleList))) ## 0, 1, 2, ..... , peopleList length
    peopleIdxCombi = list(itertools.combinations(peopleIdx, 2))
    return peopleIdxCombi

def tracking_algorithm(height, coord, frameData):
    minDistance = 150 * (height / 170)
    minDistanceIdx = -1

    # find closest person
    for idx, person in enumerate(frameData.peopleList):
        distance = calculate_distance(coord, person.get_coord())
        if minDistance > distance:
            minDistance = distance
            minDistanceIdx = idx

    # (success tracking)
    # if found 
    if minDistanceIdx != -1:
        person = frameData.poll_person(minDistanceIdx)
        person.reset(height, coord)
        return person

    # (fail tracking)
    # if not found and has candidate 
    if frameData.get_valid_len() > 0:
        id = frameData.get_valid_min()
    # if not found and has no candidate
    else :
        id = -1
    
    return Person(id, height, coord)

def distancing_algorithm(idTable, person1, person2, frameTime):
    ## get distance info
    dist = calculate_distance(person1.get_coord(), person2.get_coord())
    distHighRisk, distLowRisk = calculate_distance_threshold(person1.get_height(), person2.get_height())  ## Calculate with Image Ratio

    ## high risk
    if dist < distHighRisk:
        idTable.merge_parentIds(person1.get_id(), person2.get_id())
        if not person1.is_updated():
            person1.inc_riskTime(frameTime)
            person1.set_updated(True)
        if not person2.is_updated():
            person2.inc_riskTime(frameTime)
            person2.set_updated(True)
    
    ## low risk
    elif distHighRisk < dist and dist < distLowRisk:
        person1.set_yellow(True)
        person2.set_yellow(True)

    return

def grouping_algorithm(img, config, idTable, frameData):
    color = config.get_colors()
    imgRatio, fontScale, fontThickness, lineType, radius = config.get_figure()
    imgRatio = int(10 * imgRatio)

    for person in idTable.get_people():
        x, y = person.get_coord()

        ## Show Risk Time
        #cv2.putText(img, str(person.get_riskTime()), (x, y), 0, fontScale, color.black, fontThickness, lineType)
     
        ## Show Height
        # x1 = x - imgRatio
        # y1 = y - int(person.get_height() / 2)
        # cv2.putText(img, str(person.get_height()), (x1, y1), 0, fontScale, color.blue, fontThickness, lineType)

        ## Show Person Id   
        #cv2.putText(img, str(person.get_id()), (x1, y1), 0, fontScale, color.blue, fontThickness, lineType)
        
        ## Draw Green Circle
        if not person.is_updated():
            person.clear_riskTime()
            if person.is_yellow():
                cv2.circle(img, person.get_coord(), radius, color.yellow, -1)
            else :
                cv2.circle(img, person.get_coord(), radius, color.green, -1)
            continue
        
        ## Red
        ## Show Red Circle
        cv2.circle(img, person.get_coord(), radius, color.red, -1)

        ## Show Red Count
        # cv2.putText(img, str(person.get_redCount()), (x, y), 0, fontScale, color.red, fontThickness, lineType)
        
        ## Show Definite Risk
        if person.is_definite_risk():
            x1 = x - imgRatio
            y1 = y - int(person.get_height() / 2)
            cv2.putText(img, "RISK", (x1, y1), 0, fontScale, color.red, fontThickness, lineType)
            frameData.update_log(
                'frame : {f} | person : {i} | risk time : {t}s \n'.format(
                    f=str(frameData.get_counter()).rjust(5), 
                    i=str(person.get_id()).rjust(5), 
                    t=str(person.get_riskTime()).rjust(8)
                )
            )
        
        ## Set Group List
        idTable.set_groupList(person.get_id(), person.get_coord())

    return img

def draw_polygons(img, config, idTable):
    color = config.get_colors()
    overlay = img.copy()
    opacity = 0.5

    for polyCoords in idTable.get_groupList():
        if len(polyCoords) >= 2:
            try:
                hull = ConvexHull(polyCoords)
            except:
                pass
            else:
                polyCoords = [[polyCoords[idx]] for idx in hull.vertices]
                idTable.add_polygonArea(hull.volume)  # 20211004 fezchoi
            cv2.fillConvexPoly(overlay, np.array(polyCoords), color.red)

    cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, img)
    return img

def show_analysis(img, config, idTable, frameData):  # 20211004 fezchoi # 20211010 fezchoi
    if idTable.get_people_count() == 0:
        return img

    color = config.get_colors()
    imgRatio, fontScale, fontThickness, lineType, radius = config.get_figure()

    if frameData.get_counter() % 30 == 1:
        peopleTotal = idTable.get_people_count()
        peopleRisk  = idTable.get_high_risk_count()
        violationRate = (peopleRisk / peopleTotal)

        areaTotal = img.shape[0] * img.shape[1]
        areaPolygon = idTable.get_polygonArea()
        riskDensity = (areaPolygon / areaTotal)

        dangerLevel = violationRate * riskDensity * 100
    
        msg, clr = 'None', color.black
        
        if dangerLevel < 0.15:
            msg, clr = 'Safe  ', color.green
        elif dangerLevel < 0.25:
            msg, clr = 'Danger', color.yellow
        else :
            msg, clr = 'Hazard', color.red

        frameData.update_analysis(violationRate, riskDensity, dangerLevel, msg, clr)
    
    violationRate, riskDensity, dangerLevel, msg, clr = frameData.get_analysis()

    cv2.putText(img, 'Violation Rate  : '  + str(round(violationRate * 100, 2)).rjust(5) + '%', 
                    (500, 320), 0, fontScale, color.black, fontThickness, lineType)
    cv2.putText(img, 'Density Risk    : '  + str(round(riskDensity * 100, 2)).rjust(5) + '%', 
                    (500, 330), 0, fontScale, color.black, fontThickness, lineType)
    cv2.putText(img, 'Current Danger : '   + str(round(dangerLevel * 100, 2)).rjust(5) + '%', 
                    (500, 340), 0, fontScale, color.black, fontThickness, lineType)   
    cv2.putText(img, 'Safety Message : ' + msg, 
                    (500, 350), 0, fontScale, clr, fontThickness, lineType)
    
    return img

def show_distancing(img, boxes, frameData):

    if len(boxes) == 0:
        return img

    idTable = IdTable()
    peopleList = idTable.get_people()

    ## first frame
    if frameData.get_people_len() == 0:
        for id, box in enumerate(boxes):
            height, coord = calculate_box(box)
            peopleList.append(Person(id, height, coord))

    ## next frame
    else :
### Tracking Algorithm
        for box in boxes:
            height, coord = calculate_box(box)
            person = tracking_algorithm(height, coord, frameData)
            peopleList.append(person)

### Check Untracked people
    frameData.init_invalid()

### Distancing Algorithm
    ## create id info table
    idTable.init_idList(frameData.get_invalid())

    ## make combinations of idx
    peopleIdxCombi = create_idx_combination(peopleList)

    ## frame time
    fps = frameData.get_fps()    
    frameTime = round(1 / fps, 2) if (fps > 0.0) else 0.0

    ## distancing between two people
    for index1, index2 in peopleIdxCombi:
        person1, person2 = peopleList[index1], peopleList[index2]
        if is_valid(idTable, person1, person2):
            distancing_algorithm(idTable, person1, person2, frameTime)

### Grouping Algorithm
    config = Configs(img)
    idTable.init_groupList()
    
    img = grouping_algorithm(img, config, idTable, frameData)
    img = draw_polygons(img, config, idTable)

### Check Undetected people
    for person in frameData.get_people():
        if person.is_erasable(img.shape[:2]) or person.is_missable():
            frameData.set_valid(person.get_id())
        else :
            person.inc_missCount()
            idTable.add_person(person)

    frameData.set_people(idTable.get_people())

### Analysis
    img = show_analysis(img, config, idTable, frameData) # 20211004 fezchoi # 20211010 fezchoi

    return img
