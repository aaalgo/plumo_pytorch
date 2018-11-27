#!/usr/bin/env python
import os
import sys
import shutil
import subprocess
from glob import glob
from jinja2 import Environment, FileSystemLoader
import numpy as np
import pydicom
import os
import pickle
import cv2
from gallery import Gallery

TMPL_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                './templates')
STATIC_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                './static')
env = Environment(loader=FileSystemLoader(searchpath=TMPL_DIR))
case_tmpl = env.get_template('papaya_case.html')
index_tmpl = env.get_template('papaya_index.html')
dicom_path = 'Data/'


class Annotations:
    def __init__ (self):
        self.annos = []
        pass

    def add (self, box, hint=None):
        self.annos.append({'box': box, 'hint': hint})
        pass


def Papaya (path, case_path, annotations=Annotations()):
    try:
        os.makedirs(path)
    except:
        pass
    try:
        subprocess.check_call('rm -rf %s/dcm' % path, shell=True)
    except:
        pass
    for f in ['papaya.css', 'papaya.js']:
        shutil.copyfile(os.path.join(STATIC_DIR, f), os.path.join(path, f))
        pass
    pass
    os.mkdir(os.path.join(path, 'dcm'))
    if not os.path.isfile('%s/case.nii.gz' % (path, )):
        subprocess.check_call('./dcm2niix -z i -o %s -f case %s' % (path, case_path), shell=True)
    boxes = []
    centers = []
    for anno in annotations.annos:
        box = anno['box']
        boxes.append(box)
        z1, y1, x1, z2, y2, x2 = box
        hint = anno.get('hint', None)
        center = ((z1+z2)/2, (y1+y2)/2, (x1+x2)/2, hint)
        centers.append(center)
    with open(os.path.join(path, 'index.html'), 'w') as f:
        f.write(case_tmpl.render(boxes=boxes, centers=centers))
        pass
    pass

def nms(boxes, threshold):
    if len(boxes) == 0: return []
    pick = []
    tbox = np.transpose(boxes)
    p = tbox[0]; z = tbox[1]; y = tbox[2]; x = tbox[3]; r = tbox[4]
    idxs = np.argsort(p)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        overlap = r[i] / r[idxs[:last]]
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > threshold)[0])))
    return boxes[pick]

def draw_bb (image, y, x, r, from_dicom = False, meta=''):
    R = 10
    y0 = int(round(y-r/2-R))
    y1 = int(round(y+r/2+R))
    x0 = int(round(x-r/2-R))
    x1 = int(round(x+r/2+R))
    image = np.copy(image)
    if from_dicom:
       image = np.asarray(image)
       c = image + abs(image.min())
       image = image / image.max()
       image = np.asarray(255 * image, dtype = np.uint8)

    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(image, (x0, y0), (x1, y1), (0, 255, 0), 2)
    cv2.putText(image, str(meta), (50,50), cv2.FONT_HERSHEY_DUPLEX, 2, (0,255,0),2,cv2.LINE_AA)
    return np.flipud(image)


def papaya(samples = ['126823']):
    gal = Gallery('/output/preview', cols = 4)
    for sample in samples:
        try:
            pbb = np.load('grt123-DSB2017/bbox_result/%s_pbb.npy' % sample)
            pbb = np.asarray(pbb, np.float32)
            pbb_original = pbb[:]
            vol = np.load('grt123-DSB2017/prep_result/%s_clean.npy' % sample)
            meta = pickle.load(open('grt123-DSB2017/prep_result/'+sample+'.pickle', 'rb'))
        except:
            continue
        
        pbb = nms(pbb, 0.4)
        ii_list = pbb[:, 0].argsort()[-5:][::-1]

        extendbox = meta['extendbox']; resolution = meta['resolution']; spacing = meta['spacing']; mask_shape = meta['mask_shape']

        vol = vol[0]
        boxes = []; output_dic = {}
        anno = Annotations()
        for index, ii in enumerate(ii_list):
            p, z, y, x, r = pbb[ii,:]
            if index == 0:
                gal.text('case %s' % sample)
                cv2.imwrite(gal.next(), draw_bb(vol[int(round(z)), :, :], y, x, r))
                cv2.imwrite(gal.next(), draw_bb(vol[:,int(round(y)),:], z, x, r))
                cv2.imwrite(gal.next(), draw_bb(vol[:, :, int(round(x))], z, y, r))

            dicom_z = mask_shape[0] - int(round((z + extendbox[0][0] -r/2) * resolution[0] / spacing[0]))
            dicom_y = int(round((y + extendbox[1][0] -r/2) * resolution[1] / spacing[1]))
            dicom_x = mask_shape[2] - int(round((x + extendbox[2][0] +r/2) * resolution[2] / spacing[2]))
            dicom_r_xy = int(round(r * resolution[1] / spacing[1]))
            dicom_r_z = int(round(r * resolution[0] /spacing[0]))
            dicom_z = max(dicom_z, 0) 
            box = [max(dicom_z-dicom_r_z, 0), dicom_y, dicom_x, dicom_z , dicom_y + dicom_r_xy, dicom_x+dicom_r_xy]
            anno.add(box=box, hint='Blob %d: %.3f'%(index+1, p))

            dicom_z_to_save = int(round((z + extendbox[0][0] -r/2) * resolution[0] / spacing[0]))
            dicom_y_to_save = int(round((y + extendbox[1][0] -r/2) * resolution[1] / spacing[1]))
            dicom_x_to_save = int(round((x + extendbox[2][0] -r/2) * resolution[2] / spacing[2]))
            box_to_save = [dicom_z_to_save, dicom_y_to_save, dicom_x_to_save, dicom_z_to_save+dicom_r_z, dicom_y_to_save+dicom_r_xy, dicom_x_to_save+dicom_r_xy]
            output_dic[str(p)] = box_to_save

        papaya = Papaya('/output/papaya_' + sample, case_path = dicom_path + sample, annotations=anno)
        pickle.dump(output_dic, open('/output/boxes/%s.pickle'%sample,'wb'))
    gal.flush()
    return

if __name__ == '__main__':
    with open('grt123-DSB2017/prep_result/list') as Data:
        os.mkdir(os.path.join('/output/boxes'))
        samples = Data.readlines()
        samples = [x.strip() for x in samples]
        papaya(samples)
    # Notes:
    # 1. cooridinates used in papaya reverses x-axis and z-axis
    # 2. there may be a shift on z-axis, depending on how dicom files are sorted
