#! /usr/bin/env ruby -Ku

$chars = [*0 .. 9, *"a" .. "z", *"A" .. "Z"]

def randc
	$chars[rand($chars.size)].to_s
end

def id
	"#{randc}#{randc}#{randc}-#{randc}#{randc}-#{randc}#{randc}#{randc}"
end

ARGV[0].to_i.times do
	print "#{id}\n"
end
