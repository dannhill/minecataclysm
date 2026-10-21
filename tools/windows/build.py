#!/usr/bin/env python3
"""Configure/build captured Windows x64 runtimes with the verified LLVM-MinGW SDK."""
import argparse,json,os,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',type=Path,required=True);p.add_argument('--dependencies',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--msgfmt',type=Path,required=True);p.add_argument('--component',choices=('client','native','launcher','transport'),required=True);p.add_argument('--jobs',type=int,default=4);a=p.parse_args()
 ws=a.workspace.resolve();deps=a.dependencies.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,PATH=str(deps/'toolchain/bin')+os.pathsep+os.environ['PATH'])
 build=out/('build-'+a.component);sdk=deps/'flatbuffers/include';toolchain=ws/'tools/windows/toolchain.cmake'
 args=['cmake','-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(toolchain),'-DCMAKE_BUILD_TYPE=Release','-DCWM_FLATBUFFERS_INCLUDE_DIR='+str(sdk),'-DCMAKE_FIND_ROOT_PATH='+str(deps/'toolchain/x86_64-w64-mingw32')]
 libs={'ZLIB_INCLUDE_DIR':deps/'zlib/include','ZLIB_LIBRARY':deps/'zlib/lib/libz.dll.a'}
 if a.component=='native':
  src=ws/'cdda';targets=['cdda-server','locale'];args += ['-DTESTS=OFF','-DBUILD_TESTING=OFF','-DTILES=OFF','-DCURSES=ON','-DBACKTRACE=OFF','-DCATA_CCACHE=OFF','-DLOCALIZE=ON','-DLANGUAGES=it_IT','-DUSE_HOME_DIR=OFF','-DUSE_PREFIX_DATA_DIR=OFF','-DCMAKE_CXX_FLAGS=-DNOMINMAX -D_WIN32_WINNT=0x0A00','-DCMAKE_CXX_FLAGS_RELEASE=-O2 -g0 -DNDEBUG','-DGETTEXT_MSGFMT_BINARY='+str(a.msgfmt.resolve()),'-DLIBINTL_INCLUDE_DIR='+str(deps/'gettext/include'),'-DLIBINTL_LIBRARIES='+str(deps/'gettext/lib/libintl.dll.a'),'-DICONV_INCLUDE_DIR='+str(deps/'gettext/include'),'-DICONV_LIBRARIES='+str(deps/'gettext/lib/libiconv.dll.a')]
 elif a.component=='client':
  src=ws/'luanti';targets=['luanti','translations'];args += ['-DBUILD_CLIENT=ON','-DBUILD_SERVER=OFF','-DENABLE_LTO=OFF','-DRUN_IN_PLACE=OFF','-DENABLE_SOUND=ON','-DENABLE_GETTEXT=ON','-DENABLE_LUAJIT=OFF','-DENABLE_CURL=OFF','-DENABLE_LEVELDB=OFF','-DENABLE_REDIS=OFF','-DENABLE_POSTGRESQL=OFF','-DENABLE_PROMETHEUS=OFF','-DENABLE_SPATIAL=OFF','-DBUILD_UNITTESTS=ON','-DUSE_SDL2=OFF','-DCMAKE_CXX_FLAGS=-DNOMINMAX','-DGETTEXT_MSGFMT='+str(a.msgfmt.resolve())]
  libs.update({'PNG_PNG_INCLUDE_DIR':deps/'libpng/include','PNG_LIBRARY':deps/'libpng/lib/libpng16.dll.a','JPEG_INCLUDE_DIR':deps/'libjpeg/include','JPEG_LIBRARY':deps/'libjpeg/lib/libjpeg.dll.a','ZSTD_INCLUDE_DIR':deps/'zstd/include','ZSTD_LIBRARY':deps/'zstd/lib/libzstd.dll.a','OGG_INCLUDE_DIR':deps/'libogg/include','OGG_LIBRARY':deps/'libogg/lib/libogg.dll.a','VORBIS_INCLUDE_DIR':deps/'libvorbis/include','VORBIS_LIBRARY':deps/'libvorbis/lib/libvorbis.dll.a','VORBISFILE_LIBRARY':deps/'libvorbis/lib/libvorbisfile.dll.a','OPENAL_INCLUDE_DIR':deps/'openal/include/AL','OPENAL_LIBRARY':deps/'openal/lib/libOpenAL32.dll.a','GETTEXT_INCLUDE_DIR':deps/'gettext/include','GETTEXT_LIBRARY':deps/'gettext/lib/libintl.dll.a','FREETYPE_INCLUDE_DIR_freetype2':deps/'freetype/include/freetype2','FREETYPE_INCLUDE_DIR_ft2build':deps/'freetype/include/freetype2','FREETYPE_LIBRARY':deps/'freetype/lib/libfreetype.dll.a','SQLITE3_INCLUDE_DIR':deps/'sqlite3/include','SQLITE3_LIBRARY':deps/'sqlite3/lib/libsqlite3.dll.a'})
 elif a.component=='launcher':src=ws/'launcher';targets=['Minecataclysm']
 else:
  exe=out/'test-windows-pipe.exe';cmd=[str(deps/'toolchain/bin/x86_64-w64-mingw32-clang++'),'-std=c++17','-O2','-I'+str(ws/'protocol/include'),str(ws/'protocol/tests/test_windows_pipe.cpp'),'-ladvapi32','-o',str(exe)];subprocess.run(cmd,env=env,check=True);return
 args += ['-D'+key+'='+str(value) for key,value in libs.items()];args += ['-S',str(src),'-B',str(build)]
 commands=[args,['cmake','--build',str(build),'--target',*targets,'-j'+str(a.jobs)]]
 (out/(a.component+'-commands.json')).write_text(json.dumps(commands,indent=2)+'\n')
 for cmd in commands:subprocess.run(cmd,env=env,check=True)
if __name__=='__main__':main()
