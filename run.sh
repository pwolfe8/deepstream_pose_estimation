#!/bin/bash
DOTFOLDER=./pipeline_graphs

#rm -rf $DOTFOLDER
mkdir -p $DOTFOLDER

make

GST_DEBUG_DUMP_DOT_DIR=$DOTFOLDER  ./deepstream-pose-estimation-app /opt/nvidia/deepstream/deepstream-6.0/samples/streams/sample_720p.h264 ./

# dot -Tpdf $DOTFOLDER/pipeline.dot > pipeline.pdf
dot -Tpng $DOTFOLDER/pipeline.dot > $DOTFOLDER/pipeline.png


