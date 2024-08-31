

import shutil
import os
from os.path import getmtime
import datetime
import matplotlib.pyplot as plt
import numpy as np



def figunits(value,axis='x',fig=None):
    if fig == None: fig = plt.gcf()
    w,h = fig.get_size_inches()
    if axis=='x': return value/w
    if axis=='y': return value/h
    else: print('axis must be \'x\' or \'y\'')



def InkscapeFigure(fname, fig=None,  pdf=False, png=False):

    if fig == None: fig = plt.gcf()

    if fname[-3:]!='svg': fname+='.svg'

    if not os.path.isfile(fname):
        fig.savefig(fname, transparent=False)
        return

    # create a checkpoint in /.filename
    create_checkpoint(fname)

    # save the matplotlib file
    fig.savefig('__temp_mpl__.svg', transparent=False)
    width, height = get_figsize('__temp_mpl__.svg')

    # if needed put back to lines between blocks
    reformat_b2l('__temp_mpl__.svg')
    reformat_b2l(fname)

    # extract the figure element of the mpl file (and save it in a file __temp_elementname__.svg)
    mpl_file = create_block_file('__temp_mpl__.svg','figure_1')

    # replace the old maptplotlib block by the new one
    replace_block(fname, 'figure_1')

    # adjust the size if needed
    if get_figsize(fname) != (width,height) :
        set_figsize(fname,width,height)

    # remove temporary files
    os.remove(mpl_file)
    os.remove('__temp_mpl__.svg')

    # save fig to an other format
    if pdf: svg_to_pdf(fname)
    if png: svg_to_png(fname)

    return



def get_figsize(svgfile):
    file = open(svgfile,'r')
    lines=file.readlines()
    width = ''
    height = ''
    for l in lines:
        if 'width' in l and 'height' in l:
            for i in range(len(l)):
                if l[i:i+7]=='width="' :
                    j=i+7
                    while l[j]!='"':
                        width+=l[j]
                        j+=1

            for i in range(len(l)):
                if l[i:i+8]=='height="' :
                    j=i+8
                    while l[j]!='"':
                        height+=l[j]
                        j+=1

            break
    return width,height



def create_checkpoint(fname):
    file = fname
    path ='./'
    if '/' in fname :
        file = os.path.split(fname)[-1]
        path = os.path.split(fname)[0]
    if path[-1]!='/':path+='/'
    # keep 20 saves of the file in .file/
    if not os.path.isdir(path+'.'+file[:-4]):
        os.mkdir(path+'.'+file[:-4])
    flist=np.array(os.listdir(path+'.'+file[:-4]))
    timestamps,indexes = [],[]
    for i in range(len(flist)):
        timestamps.append(datetime.datetime.fromtimestamp(getmtime(path+'.'+file[:-4]+r'/'+flist[i])))
        indexes.append( int( flist[i] [ len(file[:-4])+1 : len(flist[i])-4 ] ) )
    timestamps,indexes=np.array(timestamps),np.array(indexes)
    flist,indexes = flist[timestamps.argsort()], indexes[timestamps.argsort()]
    timestamps = timestamps.sort()
    if len(flist)>19:
         os.remove(path+'.'+file[:-4]+r'/'+flist[0])
    if len(flist)==0:
        shutil.copy(path+file, path+'.'+file[:-4]+r'/'+file[:-4]+'_'+str(0)+'.svg')
    else :
        shutil.copy(path+file, path+'.'+file[:-4]+r'/'+file[:-4]+'_'+str(indexes.max()+1)+'.svg')

    return



def create_block_file(fname, blockid='figure_1'):
    lines = open(fname,'r').readlines()

    i,j=0,0
    str_id = 'id="'+blockid+'"'
    for i in range(len(lines)):
        if str_id in lines[i] :
            break
    if i == len(lines)-1 :
        print('id not found')
        return
    for j in range(i,-1,-1) :
        if '<' in lines[j] :
            break

    counter = 0
    f = open('__temp_'+blockid+'__.svg','w')
    for k in range(j,len(lines)) :
        l = lines[k]
        f.write(l)
        if not '<!--' in l:
            for i in range(len(l)):
                if l[i:i+2]=='</' :
                    counter-=1
                    break
                if l[i]=='<' :
                    counter+=1
                if l[i:i+2]=='/>' :
                    counter-=1

        if counter == 0 : break

    if blockid=='figure_1':
        for l in lines[k+1:]:
            if '</svg>' in l :
                break
            f.write(l)

    f.close()# -*- coding: utf-8 -*-


    return '__temp_'+blockid+'__.svg'



def set_figsize(svgfile,width,height):
    lines = open(svgfile,'r').readlines()
    done = False
    f=open(svgfile,'w')
    for l in lines:
        if 'width' in l  and not done:
            for i in range(len(l)):
                if l[i:i+7]=='width="' :
                    j=i+7
                    while l[j]!='"':
                        j+=1
                    break
            f.write(l[:i+7]+width+l[j:] )
            done = True
        else :  f.write(l)
    f.close()

    lines = open(svgfile,'r').readlines()
    done = False
    f=open(svgfile,'w')
    for l in lines:
        if 'height' in l and not done:
            for i in range(len(l)):
                if l[i:i+8]=='height="' :
                    j=i+8
                    while l[j]!='"':
                        j+=1
                    break
            f.write(l[:i+8]+height+l[j:] )
            done = True
        else :  f.write(l)

    f.close()

    lines = open(svgfile,'r').readlines()
    done = False
    f=open(svgfile,'w')
    for l in lines:
        if 'viewBox' in l and not done:
            for i in range(len(l)):
                if l[i:i+9]=='viewBox="' :
                    j=i+9
                    while l[j]!='"':
                        j+=1
                    break
            f.write(l[:i+9]+'0 0 '+width[:-2]+' '+height[:-2]+l[j:] )
            done = True
        else :  f.write(l)

    f.close()

    return



def replace_block(fname,blockid='figure_1'):
    new_block_lines = open('__temp_'+blockid+'__.svg','r').readlines()
    old_file_lines = open(fname,'r').readlines()

    i,j,k=0,0,0
    str_id = 'id="'+blockid+'"'
    for i in range(len(old_file_lines)):
        if str_id in old_file_lines[i] :
            break
    if i == len(old_file_lines)-1 :
        print('id not found')
        return
    for j in range(i,-1,-1) :
        if '<' in old_file_lines[j] :
            break

    counter = 0
    for k in range (j,len(old_file_lines)) :
        l = old_file_lines[k]
        if not '<!--' in l:
                for i in range(len(l)):
                    if l[i:i+2]=='</' :
                        counter-=1
                        break
                    if l[i]=='<' :
                        counter+=1
                    if l[i:i+2]=='/>' :
                        counter-=1

        if counter == 0 : break

    f = open(fname,'w')
    #ff = open('__old_file_lines__.svg','w')
    for l in old_file_lines[:j] :
        f.write(l)
    #    ff.write(l)

    for l in new_block_lines:
        f.write(l)

    for l in old_file_lines[k+1:]:
        f.write(l)
    #    ff.write(l)

    f.close()
    return



def reformat_b2l(fname):
    lines = open(fname,'r').readlines()
    f = open(fname,'w')
    new_lines = []
    b2l = lines[0][-1]
    add_line = True
    i=0
    while i < len(lines):
        if add_line: new_lines.append(lines[i])
        l = new_lines[-1]
        for j in range(len(l)):
            add_line = True
            if l[j:j+2]=='><':
                new_lines[-1]= l[:j+1]+b2l
                new_lines.append(l[j+1:])
                add_line = False
                break
        if j==len(l)-1:
            add_line = True
            i+=1
    for l in new_lines: f.write(l)
    f.close()



def svg_to_pdf(fname):
    """ Needs inkscape in the path to work ! """
    try:
        if os.name == 'nt':
            cmd = 'inkscape.exe --without-gui --export-area-page --file="'+fname+'" --export-pdf="'+fname[:-3]+'.pdf" --export-dpi=72.27'
        else:
            cmd = 'inkscape --without-gui --export-area-page --file="'+fname+'"  --export-type "pdf" --export-dpi 72.27'
        os.system(cmd)
    except:
        print('export to pdf failed')

def svg_to_png(fname):
    """ Needs inkscape in the path to work ! """
    try:
        if os.name == 'nt':
            cmd = 'inkscape.exe --without-gui --export-area-page --file="'+fname+'" --export-png="'+fname[:-3]+'.png" --export-dpi=72.27'
        else:
            cmd = 'inkscape --without-gui --export-area-page --file="'+fname+'"  --export-type "png" --export-dpi 72.27'
        os.system(cmd)
    except:
        print('export to png failed')







