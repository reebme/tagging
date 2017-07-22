def read_new_tags( tag_file ):
	"""
	Read tags and values for files from csv tag_file
	return list
	csv file format:
	empty\ttagname\ttagname...
	filename\ttagvalue\ttagvalue...
	"""
	in_tags = [ line.strip( '\n' ).decode( "utf-8" ).split( '\t' )
			for line in open( tag_file ) ]
	return in_tags

def find_file_by_name( file_name, list_of_files ):
	"""
	Find file in given list.
	Return path to file file_name.
	list_of_files is a list of tuples ( dirpath, short_name, ext )
	dirpath - directory in which file short_name is located
	ext - short_name file extension
	"""
