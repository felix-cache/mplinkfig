import shutil
import os
from os.path import getmtime
import datetime
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display, SVG
from lxml import etree


def figunits(value,axis='x',fig=None):
    """ convert inches to figure units (fraction of the width if axis='x', height if axis='y') """
    if fig == None: fig = plt.gcf()
    w,h = fig.get_size_inches()
    if axis=='x': return value/w
    if axis=='y': return value/h
    else: print('axis must be \'x\' or \'y\'')



def InkFig(fig, fname, transparent=False, show=False, pdf=False, png=False):
    """ actualize the figure elements created with matplotlib while keeping the changes perforemd with inkscape """

    if fname[-3:]!='svg': fname+='.svg'

    if not os.path.isfile(fname):
        fig.savefig(fname, transparent=transparent)
        return

    # create a checkpoint in /.filename
    create_checkpoint(fname)

    # save the matplotlib file
    fig.savefig('__temp_mpl__.svg', transparent=transparent)
    width, height = get_figsize('__temp_mpl__.svg')

    # replace the mpl block of the inkscape file with the one from the new matplotlib figure
    replace_mpl_figure_block(fname, '__temp_mpl__.svg', 'figure_1')

    # adjust the size if needed
    if get_figsize(fname) != (width,height) :


    # remove temporary file
    os.remove('__temp_mpl__.svg')

    # save fig to an other format
    if pdf: svg_to_pdf(fname)
    if png: svg_to_png(fname)

    # show inkscape part
    if show:
        showSVG(fname)
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




def replace_mpl_figure_block(inkscape_svg, mpl_svg, blockid='figure_1'):

    parser = etree.XMLParser(remove_blank_text=False)

    # Load both SVGs
    tree_ink = etree.parse(inkscape_svg, parser)
    root_ink = tree_ink.getroot()

    tree_mpl = etree.parse(mpl_svg, parser)
    root_mpl = tree_mpl.getroot()

    ns = root_ink.nsmap.copy()
    if None in ns:
        ns['svg'] = ns.pop(None)

    # Find <g id="figure_1"> in both
    xpath = f'.//svg:g[@id="{blockid}"]'
    block_mpl = root_mpl.xpath(xpath, namespaces=ns)
    block_ink = root_ink.xpath(xpath, namespaces=ns)

    if not block_mpl:
        raise ValueError(f'Block id="{blockid}" not found in {mpl_svg}')
    if not block_ink:
        raise ValueError(f'Block id="{blockid}" not found in {inkscape_svg}')

    block_mpl = block_mpl[0]
    block_ink = block_ink[0]

    # Replace the Inkscape block with the Matplotlib one
    parent = block_ink.getparent()
    parent.replace(block_ink, block_mpl)

    # Write back to the Inkscape file
    tree_ink.write(inkscape_svg, encoding='utf-8',


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

def fix_xml_space(svgfile):
    with open(svgfile, 'r') as f:
        content = f.read()
    content = content.replace('xml:space="preserve"', 'xml:space="default"')
    with open(svgfile, 'w') as f:
        f.write(content)


def svg_to_pdf(fname):
    """ Needs inkscape in the path to work ! """
    if fname[-4:]=='.svg' : fname=fname[:-4]

    ik = 'inkscape'
    if os.name == 'nt':ik+='.exe'

    try:
        cmd = ik+' '+fname+'.svg -o '+fname+'.pdf'
        os.system(cmd)
    except:
        print('export to pdf failed')


def svg_to_png(fname):
    """ Needs inkscape in the path to work ! """
    if fname[-4:]=='.svg' : fname=fname[:-4]

    ik = 'inkscape'
    if os.name == 'nt':ik+='.exe'

    try:
        cmd = ik+' '+fname+'.svg -o '+fname+'.png'
        os.system(cmd)
    except:
        print('export to png failed')


def showSVG(fname):
    if fname[-4:]!='.svg' : fname+='.svg'
    try:
        display(SVG(fname))
    except:
        print('error')






'''
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


def InkFig(fig, fname, transparent=False, show=False, pdf=False, png=False):
    """ actualize the figure elements created with matplotlib while keeping the changes perforemd with inkscape """

    if fname[-3:]!='svg': fname+='.svg'

    if not os.path.isfile(fname):
        fig.savefig(fname, transparent=transparent)
        return

    # create a checkpoint in /.filename
    create_checkpoint(fname)

    # save the matplotlib file
    fig.savefig('__temp_mpl__.svg', transparent=transparent)
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

    replace xml:space="preserve" by xml:space="default"
    fix_xml_space(fname)

    # remove temporary files
    os.remove(mpl_file)
    os.remove('__temp_mpl__.svg')

    # save fig to an other format
    if pdf: svg_to_pdf(fname)
    if png: svg_to_png(fname)

    # show inkscape part
    if show:
        #fig.set_visible(False)
        showSVG(fname)
    return

'''
