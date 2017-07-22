#!/usr/bin/python
#-*- coding: windows-1250 -*-

import argparse

import sys

import libtagaudio as lta

from os import walk, rename
from os.path import join, isfile, isdir, islink, split

from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

parser = argparse.ArgumentParser()

#positional
parser.add_argument( "paths", nargs = '+', help = "directories with music and music files" )

#TODO - arguments
#optional
#files in table view (default) or files in list
parser.add_argument( "-l", "--horizontal", help = "list of music files with tags", action = "store_true" )
#choice of tags which are displayed (all/existing/of choice)
parser.add_argument( "-c", "--choose_tags", help = "display all available tags", choices=[ "all", "existing", "choice" ], default="all" )
#write output to screen (default) of to a file
parser.add_argument( "-o", "--output", nargs = "?", type = argparse.FileType( "w" ), default = sys.stdout , help = "output file" )
#no output
parser.add_argument( "-q", "--quiet", help = "shhhhh...", action = "store_true" )
#fill tags from file
parser.add_argument( "-f", "--fill_from_file", help = "file with tags" )
#TODO pattern in configuration file
#change name of files acording to pattern - now track_no_track_title.extension
parser.add_argument( "-n", "--names", help = "change names to track_no_track_title.extension", choices = [ "tryout", "doit" ] )
#change track numbers to format 0n
parser.add_argument( "-z", "--zero", help = "change track number format to 0n for numbers < 10", action = "store_true" )

args = parser.parse_args()

#if args.horizontal:
#	print "List view on."
#if args.choose_tags:
#	print "{} tags will be displayed.".format( args.choose_tags )
#print args.output
#
#
#print args.dirs

#TODO to .tagging_config
audio_ext = set( [ 'flac', 'mp3' ] )

flac_tags = [
	"artist",
	"album",
	"title",
	"tracknumber",
	"date",
	"genre",
	"copyright",
	"license",
]

#audio_files - list of tuples( path, name, extension )
def get_tags( audio_files ):
	audio_files_tags = [ [ "Nazwa pliku" ] + flac_tags ]
	for dirpath, short_name, ext in audio_files:
		full_name = join( dirpath, short_name )
		if ext == "flac":
			audio_file = FLAC( full_name )
			audio_file_tags = [ short_name ]
			for tag in flac_tags:
				audio_file_tags.append( ",".join( audio_file.get( tag, "" ) ) )
			audio_files_tags.append( audio_file_tags )
		#if ext == "mp3":
		#	audio_file = ID3( full_name )
		#	audio_file_tech = MP3( full_name )
		#	print "{}, {}".format( short_name, audio_file_tech.info.bitrate )
	return audio_files_tags


#FIXME repeating entries removal
files_in_dirs = []
ext = ""
for in_path in args.paths:
	if isdir( in_path ):
		#print "Directory:\n{}".format( in_path )
		for dirpath, dirnames, filenames in walk( in_path ):
			for short_name in filenames:
				file_name, ext = short_name.rsplit(  ".", 1 )
				if ext in audio_ext:
					files_in_dirs.append( ( dirpath, short_name, ext ) )
	elif isfile( in_path ):
		dirpath, short_name = split( in_path )
		if dirpath == "":
			dirpath = "."
		filename, ext = in_path.rsplit( ".", 1 )
		if ext in audio_ext:
			files_in_dirs.append( ( dirpath, short_name, ext ) )
		#print "File:\ndirpath: {}, short_name: {}, ext: {}".format( dirpath, short_name, ext )
	elif islink( in_path ):
		#TODO do not follow soft links (omitting...)
		print "Link:\n{}".format( in_path )
#print "\n".join( "{}".format( join( fid[0], fid[1] ) ) for fid in files_in_dirs )

#TODO filling tags from lists of values - how lists of values are treated in cowon
if args.fill_from_file:
	in_tags = lta.read_new_tags( args.fill_from_file )
	print in_tags
	#for every file in files_in_dirs fill tags as given in args.fill_from_file
#	for dirpath, short_name, ext in files_in_dirs:
#		full_name = join( dirpath, short_name )
#		if ext == "flac":
#			audio_file = FLAC( full_name )
#			track_no = audio_file[ "tracknumber" ][0].split( "/", 1 )[0]
#			#FIXME vulnerable for not having vorbis tag section and for not having a tag?
#			for tag, tag_value in in_tags:
#				#if tag is number, value is track title, else it's just tag
#				if tag.isdigit() and tag == track_no:#FIXME mrauczatka
#					audio_file[ "title" ] = tag_value
#				else:
#					audio_file[ tag ] = tag_value
#			audio_file.save()

if args.zero:
	print "Refpormatting track numbers..."
	for dirpath, short_name, ext in files_in_dirs:
		full_name = join( dirpath, short_name )
		if ext == "flac":
			audio_file = FLAC( full_name )
			track_no = audio_file[ "tracknumber" ][0].split( "/", 1 )[0]
			if track_no > 100:#FIXME mrauczatka modulo 100
				track_no = "".join( list( str( track_no ) )[-2:] )
			audio_file[ "tracknumber" ] = track_no.zfill( 2 )
			audio_file.save()

if args.names:
	replacements = {
		" ":"_",
		"'":"",
		"=":"_",
		".":"",
		"(":"",
		")":"",
		"[":"",
		"]":"",
		"!":"",
		"/":"_",
		"feat":"ft",
		"Feat":"ft",
		"&":"and",
	}
	print "Changing names..."
	for dirpath, short_name, ext in files_in_dirs:
		if ext == "flac":
			audio_file = FLAC( join( dirpath, short_name ) )
			
			#zmień nazwy zgodnie z tagami (nr_tytuł)
			new_short_name = []
			#nr ścieżki
			try:
				#TODO iteracja po tagach FLAC
				#TODO co jeśli nr ścieżki jest bez liczby ścieżek?
				track_no = audio_file[ "tracknumber" ][0].split( "/", 1 )[0]
				#nr uzupełniony o 0 na początku, jeśli < 10
				new_short_name = [ track_no.zfill( 2 ) ]
				#tytuł
				new_short_name.extend( audio_file[ "title" ] )
			except KeyError as ke:
				print "Brak tagu {}".format( ke )

			#list->string
			new_short_name = "_".join( new_short_name )
			#formatowanie nazwy
			for replaced, replacing in replacements.iteritems():
				new_short_name = new_short_name.replace( replaced, replacing )
			
			#nowa nazwa pliku wraz ze ścieżką
			new_name = "{}.flac".format( join( dirpath, new_short_name ) )
			
			#zmień nazwę
			if args.names == "tryout":
				print "{:_^75}".format( "" )
				print "{:^75}".format( short_name )
				print "rename(\n{},\n{} )".format( join( dirpath, short_name ), new_name )
			elif args.names == "doit":
				rename( join( dirpath, short_name ), new_name )

#FIXME no sense after name change
if not args.quiet:
	flac_files = get_tags( files_in_dirs )
	for row in flac_files:
	#TODO wyświetlanie uwzględniające znaki spoza ascii (kodowanie utf-8)
	#wylicz szerokość kolumn
	#print "\n".join( [ ", ".join( map( str, flac_files_col_width[ i ] ) ) for i in range( len( flac_files_col_width ) ) ] )
		flac_files_col_width = [ max( [ len( flac_files[ i ][ j ] ) 
					for i in range( len( flac_files ) ) ] ) 
				 for j in range( len( flac_files[ 0 ] ) ) ]
	#print flac_files_col_width

	#stworz str do str.format()
	flac_files_head = list( flac_tags )
	flac_files_head.insert( 0, "name" )
	flac_cols = zip( flac_files_head, flac_files_col_width )
	format_flac_files_row = []
	for tag, width in flac_cols:
		#TODO * (rozwijanie listy)
		format_flac_files_row.append( "{{0[{}]:<{}}}".format( flac_cols.index( ( tag, width ) ), width ) )
	format_flac_files_row = "|".join( format_flac_files_row )
	#print format_flac_files_row
	for row in flac_files:
		print format_flac_files_row.format( row )
