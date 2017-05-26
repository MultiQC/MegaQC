module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    
    // JavaScript minification
    bower_concat: {
      all: {
        dest: {
          'js': 'build/_bower.js'
        },
        dependencies: {
          'bootstrap': 'jquery'
        },
        bowerOptions: {
          relative: false
        }
      }
    },
    concat: {
      extras: {
        src: ['build/_bower.js', 'megaqc/static/js/script.js'],
        dest: 'build/_concat.js',
      },
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: 'build/_concat.js',
        dest: 'megaqc/static/public/js/megaqc.min.js'
      }
    },
    
    // SCSS and CSS tasks
    sass: {
      dist: {
        options: {
          style: 'compressed',
          sourcemap: 'none',
          trace: true
        },
        files: { // 'destination': 'source'
          'megaqc/static/public/css/main.css': 'megaqc/static/scss/main.scss'
        }
      }
    },
    copy: {
      main: {
        files: [{
          expand: true,
          src: ['megaqc/static/libs/font-awesome/fonts/*'],
          dest: 'megaqc/static/public/fonts/',
          filter: 'isFile',
          flatten: true
        }],
      }
    },
    
    // watch and exec commands
    watch: {
      less: {
        files: [ 'bower.json' ],
        tasks: [ 'exec:bower_install' ]
      },
      app_js: {
        files: ['megaqc/static/js/script.js'],
        tasks: ['concat','uglify']
      },
      app_scss: {
        files: [
          'megaqc/static/scss/main.scss',
          'megaqc/static/scss/variables.scss',
          'megaqc/static/scss/core.scss',
          'megaqc/static/scss/app.scss',
        ],
        tasks: ['sass']
      }
    },
    exec: {
      bower_install: {
        cmd: 'bower install'
      }
    }
  });

  // Load the plugins
  grunt.loadNpmTasks('grunt-subgrunt');
  grunt.loadNpmTasks('grunt-bower-concat');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.loadNpmTasks('grunt-contrib-copy');

  // Default task.
  grunt.registerTask('default', ['bower_concat','concat','uglify','sass','copy']);

};