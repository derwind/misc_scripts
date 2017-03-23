#! /usr/bin/env ruby -Ku

INCLUDE_PATTERN = %r"^\s*include\s*\(\s*(\S+)\s*\)"

path = ARGV[0]
dirname = File.dirname(path)

File.open(path) { |f|
	while line = f.gets
		if line =~ /#{INCLUDE_PATTERN}/
			print File.read(File.join(dirname, $1))
		else
			print
		end
	end
}
