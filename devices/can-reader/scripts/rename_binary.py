Import("env")

env.Replace(PROGNAME="firmware_%s" % env.GetProjectOption("device_type"))