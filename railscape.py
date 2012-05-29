# Railscape
# Converts  database schemas from Rails to Django models
#
import re
import shlex
import pprint


def create_model(modelname):
    print "Creating model", modelname
    return {'model' : modelname, 'fields' : [] }

def add_model_fields(models, line, current_model):
    models[current_model]['fields'].append({'field' : parse_line(line)})

def parse_line(line):
    line = shlex.split(line)

    # switching
    options = {
        't.integer': int_field,
        't.string': string_field,
        't.text': text_field,
        't.datetime': datetime_field,
        't.date': date_field,
        't.boolean': bool_field,
    }
    # return any ugly commas before checking against the options dict
    return options[line[0]](line[1].replace(',',''), extra_args(line))

def extra_args(args):
    print "extra args", args
    if len(args) > 2:
        # we have more args to take care of
        # extra args comes in the form :key => 'value'
        # therefor we can assume they come in chunks of 3 (three) items

        # remove non wanted elements such as simple commas and empty strings
        #for a in args:
        #    if a in [",", ""]:
        #        print "removing", a
        #        args.remove(a)
        #        print "args after remove", args
        # remove the two first items from the list
        args = args[1:-1]
        # make sure we have a list consisting of three's (multiples of 3)
        print "len", len(args), args
        if len(args) % 3 == 0:
            k = a = v = ''
            for i in range(len(args), 3):

                k = args[0+i]
                a = args[1+i]
                v = args[2+i]
                print ">>", k, a, v
                # TODO: Implement the extra args here

    return None

def xa(a):
    return '' if a is None else a

def int_field(n, args=None):
    return '%s = models.IntegerField(verbose_name="%s", %s)' % (n , n, xa(args))
def string_field(n, args=None):
    return '%s = models.CharField(verbose_name="%s", max_length=255, %s)' % (n , n, xa(args))
def text_field(n, args=None):
    return '%s = models.TextField(verbose_name="%s", %s)' % (n , n, xa(args))
def datetime_field(n, args=None):
    return '%s = models.CharField(verbose_name="%s", max_length=255, %s)' % (n , n, xa(args))
def date_field(n, args=None):
    return '%s = models.DateField(verbose_name="%s", %s)' % (n , n, xa(args))
def bool_field(n, args=None):
    return '%s = models.BooleanField(verbose_name="%s", %s)' % (n , n, xa(args))


def convert(filename=None):
    if not filename:
        print "Using default filename 'schema.rb'"
        filename = 'schema.rb'
    try:
        f = open(filename, "r")
    except IOError as (errno, strerror):
        #print "I/O error({0}): {1}".format(errno, strerror)
        print "Could not open requested file", filename
        raise

    modelname = ''
    old_modelname = ''
    current_model = 0    # index for which model we're currently modifying

    models = []

    # program entry
    for line in f:

        # clean up the string a bit
        line = line.lstrip()
        # strip multiple spaces
        line = re.sub('\s{2,}', ' ', line)

        # handle comments
        if "#" in line:
            line, comment = line.split("#", 1) #TODO: this breaks hash tags in strings

        if line.startswith("create_table"):
            # start of model
            modelname = line.split(" ")[1].replace('"', '')
            models.append(create_model(modelname))

        elif line.startswith("end"):
            # end of model
            print "model %s complete" % modelname
            old_modelname = modelname
            current_model = current_model + 1

        # populate model with fields
        elif old_modelname != modelname:
            add_model_fields(models, line, current_model)

    print "Finished with conversion"
    return  models


def build_django_models_file(models):

    # Django models will be stored in this file

    f = open("models.py", "w");

    top_text = "#-*- coding:utf-8 -*-\n__author__='Railscape'\nfrom django.db import models\n\n"
    f.write(top_text)
    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(models)

    for model in models:

        # TODO: Don't strip any unwanted commas' here, do it properly at the correct location
        model_class_text = "class %s(models.Model):\n" % model['model'].title().replace(',', '') # last minute hack to get unwanted comma out of the way
        f.write(model_class_text)

        for field in model['fields']:
            field_text = "    %s\n" % field['field']
            f.write(field_text)
        # and after this class we want some spaces inserted
        f.write("\n\n")


if __name__ == "__main__":

    from optparse import OptionParser
    usage = "usage: %prog [options] arg1 arg2 "
    parser = OptionParser(usage, version="%prog 0.1")
    parser.add_option('-f', '--file', dest='filename', help='Rails schema file to convert')
    (options, args) = parser.parse_args()

    if len(args) != 1:
        print "args != 1"
    if options.filename:
        models = convert(options.filename)
    else:
        models = convert()

    build_django_models_file(models)
