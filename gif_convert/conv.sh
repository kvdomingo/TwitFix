#!/bin/bash -e

usage(){
    echo "Usage: $0 [options] output"
    echo "Options:"
    echo "  --help              Show this help"
    echo "  -u, --url           URL of the video"
    echo "  -w, --max-width     Maximum width of the output"
    echo "  -h, --max-height    Maximum height of the output"
    echo "  -t, --threads       Number of threads to use"
    exit 1
}

URL=""
MAXW=400
MAXH=267
THREADS=1
OUTPUT="out.gif"
FPS=10

while [ $# -gt 0 ]; do
    case "$1" in
        --help)
            usage
            ;;
        -u|--url)
            URL="$2"
            shift
            ;;
        -w|--max-width)
            MAXW="$2"
            shift
            ;;
        -h|--max-height)
            MAXH="$2"
            shift
            ;;
        -t|--threads)
            THREADS="$2"
            shift
            ;;
        -f|--fps)
            FPS="$2"
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            ;;
        *)
            OUTPUT="$1"
            ;;
    esac
    shift
done

# make unique temp directory
TEMPDIR=$( mktemp -d )

./ffmpeg -i "$URL" -vf "scale=if(gte(iw\,ih)\,min($MAXW\,iw)\,-2):if(lt(iw\,ih)\,min($MAXH\,ih)\,-2)" -threads $THREADS "$TEMPDIR/frame%04d.png"
./gifski -o "$TEMPDIR/out.gif" --fast --fps $FPS --quality=90 $TEMPDIR/frame*.png
#./gifsicle -O3 "$TEMPDIR/out.gif" -o "$OUTPUT"
mv "$TEMPDIR/out.gif" "$OUTPUT"
rm -rf "$TEMPDIR"
