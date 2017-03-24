#! /usr/bin/env ruby -Ku

basedir = ARGV[0]

Dir::glob(File.join(basedir, "**/*.pyc")) { |f|
	basename = File.basename(f, ".pyc")
	dirname = File.dirname(f)
	cmd = "uncompyle2 -o #{File.join(dirname, basename)}.py #{f}"
	system(cmd)
}
