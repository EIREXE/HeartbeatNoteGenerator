import json
import argparse
from lxml import etree
import tinycss
from copy import deepcopy
import numpy
import colorsys
import os
import subprocess

def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v

def make_target_style(tree) -> str:
   FILTER = """
       <filter
       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
       inkscape:collect="always"
       style="color-interpolation-filters:sRGB"
       id="backFilter"
       x="-0.15193133"
       width="1.3038627"
       y="-0.099159664"
       height="1.1983193">
      <feGaussianBlur
         inkscape:collect="always"
         stdDeviation="2.433064"
         id="gaussianBlurBack" />
    </filter>
   """

   FG_STYLE = "fill:#272646;fill-opacity:1;stroke:#ffffff;stroke-width:2;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:none"
   
   main_layer = tree.getroot().find('g', {None: "http://www.w3.org/2000/svg"})
   main_path = tree.getroot().find('g', {None: "http://www.w3.org/2000/svg"})[0]
   defs = tree.getroot().find('defs', {None: "http://www.w3.org/2000/svg"})

   main_path.set('style', FG_STYLE)

   defs.append(etree.fromstring(FILTER))

   BG_STYLE = "fill:#ffffff;fill-opacity:1;stroke:#ffffff;stroke-width:2.0;stroke-opacity:1;filter:url(#backFilter);"
   bg_path = deepcopy(main_path)
   bg_path.set('style', BG_STYLE)
   main_layer.insert(0, bg_path) 

   return tree.getroot()

def make_multi_note_style(tree, color) -> str:
   OUTLINE_COLOR = '#e7ba3f'
   root = make_normal_style(tree, color)
   outline_path = root.find('g', {None: "http://www.w3.org/2000/svg"})[-1]
   outline_path.set('style', outline_path.get('style').replace('stroke:#000000', 'stroke:' + OUTLINE_COLOR).replace('stroke-width:2.0', 'stroke-width:4.0'))
   return root
def make_multi_note_target_style(tree) -> str:
   BG_LINEAR_GRADIENT = """
       <linearGradient
       inkscape:collect="always"
       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
       id="bgLinearGradient">
      <stop
         style="stop-color:#f94723;stop-opacity:1"
         offset="0"
         id="stop844" />
      <stop
         style="stop-color:#b10000;stop-opacity:1"
         offset="1"
         id="stop846" />
    </linearGradient>
   """
   BG_RADIAL_GRADIENT = """
       <radialGradient
       xmlns:xlink="http://www.w3.org/1999/xlink"
       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
       inkscape:collect="always"
       xlink:href="#bgLinearGradient"
       id="bgRadialGradient"
       cx="49.999999"
       cy="50.000001"
       fx="49.999999"
       fy="50.000001"
       r="40.248082"
       gradientTransform="matrix(1,0,0,1.5050907,0,-25.254534)"
       gradientUnits="userSpaceOnUse" />
   """
   OUTLINE_COLOR = '#e7ba3f'
   root = make_target_style(tree)
   main_layer = root.find('g', {None: "http://www.w3.org/2000/svg"})
   bg_path = root.find('g', {None: "http://www.w3.org/2000/svg"})[0]
   main_path = root.find('g', {None: "http://www.w3.org/2000/svg"})[1]
   defs = root.find('defs', {None: "http://www.w3.org/2000/svg"})
   
   defs.append(etree.fromstring(BG_LINEAR_GRADIENT))
   defs.append(etree.fromstring(BG_RADIAL_GRADIENT))
   bg_path.set('style', bg_path.get('style').replace('fill:#ffffff', 'fill:' + OUTLINE_COLOR).replace('stroke:#ffffff', 'fill:' + OUTLINE_COLOR))
   main_path.set('style', main_path.get('style').replace('stroke:#ffffff', 'stroke:' + OUTLINE_COLOR))
   main_path.set('style', main_path.get('style').replace('fill:#272646', "fill:url(#bgRadialGradient);"))
   main_path.set('style', main_path.get('style').replace('stroke-width:2', "stroke-width:4"))
   

   return root

def make_hold_target_style(tree, color) -> str:
   FILTER = """
       <filter
       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
       inkscape:collect="always"
       style="color-interpolation-filters:sRGB"
       id="backFilter"
       x="-0.15193133"
       width="1.3038627"
       y="-0.099159664"
       height="1.1983193">
      <feGaussianBlur
         inkscape:collect="always"
         stdDeviation="2.433064"
         id="gaussianBlurBack" />
    </filter>
   """
   
   FG_STYLE = "fill:#272646;fill-opacity:1;stroke:" + "#" + color + ";stroke-width:3;stroke-opacity:1;stroke-miterlimit:4;stroke-dasharray:none"
   
   main_layer = tree.getroot().find('g', {None: "http://www.w3.org/2000/svg"})
   main_path = tree.getroot().find('g', {None: "http://www.w3.org/2000/svg"})[0]
   defs = tree.getroot().find('defs', {None: "http://www.w3.org/2000/svg"})

   main_path.set('style', FG_STYLE)

   defs.append(etree.fromstring(FILTER))

   BG_STYLE = "fill:#ffffff;fill-opacity:1;stroke:#ffffff;stroke-width:2.0;stroke-opacity:1;filter:url(#backFilter);"
   bg_path = deepcopy(main_path)
   bg_path.set('style', BG_STYLE)
   main_layer.insert(0, bg_path) 

   return tree.getroot()

def make_normal_style(tree, color) -> str:
   CLIP_PATH = """
      <clipPath
         xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
         clipPathUnits="userSpaceOnUse"
         id="clipPathShadow">
      </clipPath>
   """

   COLOR = "87d639"
   COLOR2="ace376"
   STYLE = "fill:none;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:2.0;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"

   SHADOW_PATH = """
    <circle
       style="opacity:1;vector-effect:none;fill:#f3cc72;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:4.5188508;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1"
       id="path1437"
       r="147.14287"
       cy="-44.285713"
       cx="-61.785709" />
"""

   main_layer = tree.getroot().find('g', {None: "http://www.w3.org/2000/svg"})
   main_path = tree.getroot().find('g', {None: "http://www.w3.org/2000/svg"})[0]
   defs = tree.getroot().find('defs', {None: "http://www.w3.org/2000/svg"})

   ## add shadow

   # create path and clip path (from the note shape we have)

   clip_path_path = deepcopy(main_path)
   clip_path = etree.fromstring(CLIP_PATH)
   clip_path.append(clip_path_path)

   # calculate shadow color
   rgb = tuple(int(COLOR[i:i+2], 16) for i in (0, 2, 4))
   rgb2 = tuple(int(COLOR2[i:i+2], 16) for i in (0, 2, 4))
   test = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

   hsv1 = colorsys.rgb_to_hls(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
   hsv2 = colorsys.rgb_to_hls(rgb2[0]/255.0, rgb2[1]/255.0, rgb2[2]/255.0)
   hsvtest = colorsys.rgb_to_hls(test[0]/255.0, test[1]/255.0, test[2]/255.0)

   shadow_color_hls = numpy.subtract(hsvtest, numpy.subtract(hsv1, hsv2))
   shadow_rgb = colorsys.hls_to_rgb(shadow_color_hls[0], shadow_color_hls[1], shadow_color_hls[2])

   out_rgb = '#%02x%02x%02x' % (int(shadow_rgb[0]*255), int(shadow_rgb[1]*255), int(shadow_rgb[2]*255))

   shadow = etree.fromstring(SHADOW_PATH)
   shadow.set('style', STYLE.replace('fill:none', 'fill:' + out_rgb))
   shadow.set('clip-path', 'url(#clipPathShadow)')

   main_layer.append(shadow)
   defs.append(clip_path)

   ## add outline only clone of main shape

   top_outline = deepcopy(main_path)


   top_outline.set('style', STYLE.replace('stroke:none', 'stroke:#000000'))
   main_layer.append(top_outline)

   # set default color

   main_path.set('style', STYLE.replace('fill:none', 'fill:#' + color))

   #print(main_path.get('style'))
   return tree.getroot()


def get_style_prop(style_str: str, prop):
   items = style_str.split(';')
   for item in items:
      if item.startswith('prop'):
         return item.split(':')[1]

def export_png(svg_path, small=False):
   png_path = os.path.splitext(svg_path)[0] + ".png"
   small_png_path = os.path.splitext(svg_path)[0] + "_small.png"
   SIZE = 128
   SIZE_SMALL = 64
   subprocess.run(['inkscape', '-z', '-f', svg_path, '-w', str(SIZE), '--export-area-page', '-e', png_path])
   if small:
      subprocess.run(['inkscape', '-z', '-f', svg_path, '-w', str(SIZE_SMALL), '--export-area-page', '-e', small_png_path])
if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Project Heartbeat note generator')
   parser.add_argument('--input', help="Definition file for parsing")
   args = parser.parse_args()
   config_path = os.path.join(args.input, "icon_pack.json")
   if os.path.isfile(config_path):
      with open(config_path, 'r') as file:
         data = json.loads(file.read())
         src_path = os.path.join(args.input, 'src')
         for graphic_name in data['graphics']:
            graphic = data['graphics'][graphic_name]
            for subgraphic_name in graphic['src']:
               
               subgraphic = graphic['src'][subgraphic_name]
               graphic_path = os.path.join(src_path, subgraphic['src_path'] + '.svg')
               if os.path.isfile(graphic_path):
                  out_path = os.path.join(args.input, subgraphic['target_path'] + '.svg')
                  print("OUTPUTTING " + out_path)
                  os.makedirs(os.path.dirname(out_path), exist_ok=True)
                  tree = etree.parse(graphic_path)

                  if subgraphic['style'] == 'normal':
                     result = make_normal_style(tree, graphic['color'].replace('#', ''))
                  if subgraphic['style'] == 'target':
                     result = make_target_style(tree)
                  if subgraphic['style'] == 'hold_target':
                     result = make_hold_target_style(tree, graphic['color'].replace('#', ''))
                  if subgraphic['style'] == 'multi_note':
                     result = make_multi_note_style(tree, graphic['color'].replace('#', ''))
                  if subgraphic['style'] == 'multi_note_target':
                     result = make_multi_note_target_style(tree)
                  out = open(out_path, 'w')
                  if result:
                     out.write(etree.tostring(result, encoding='unicode'))
                     out.close()
                     if subgraphic['style'] == 'normal':
                        export_png(out_path, small=True)
                     else:
                        export_png(out_path, small=False)

   else:
      print("Cannot find icon pack at path {}".format(config_path))