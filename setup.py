from setuptools import setup, Extension
# via: https://stackoverflow.com/a/66479252
setup_args = dict(
	ext_modules = [
		Extension(
			'catchall.ext',
			['lib/stddev.cpp'],
			include_dirs = ['lib'],
			py_limited_api = True
		)
	]
)
setup(**setup_args)