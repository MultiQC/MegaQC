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
        src: ['build/_bower.js', 'multiqc_db/static/js/script.js'],
        dest: 'build/_concat.js',
      },
    },
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: 'build/_concat.js',
        dest: 'multiqc_db/static/public/js/multiqc_db.min.js'
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
          'multiqc_db/static/public/css/main.css': 'multiqc_db/static/scss/main.scss'
        }
      }
    },
    copy: {
      main: {
        files: [{
          expand: true,
          src: ['multiqc_db/static/libs/font-awesome/fonts/*'],
          dest: 'multiqc_db/static/public/fonts/',
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
        files: ['multiqc_db/static/js/script.js'],
        tasks: ['concat','uglify']
      },
      app_scss: {
        files: [
          'multiqc_db/static/scss/main.scss',
          'multiqc_db/static/scss/variables.scss',
          'multiqc_db/static/scss/core.scss',
          'multiqc_db/static/scss/app.scss',
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