



/*********************************************************************
 * (C) Copyright 2001 Albert Ludwigs University Freiburg
 *     Institute of Computer Science
 *
 * All rights reserved. Use of this software is permitted for 
 * non-commercial research purposes, and it may be copied only 
 * for that use.  All copies must include this copyright message.
 * This software is made available AS IS, and neither the authors
 * nor the  Albert Ludwigs University Freiburg make any warranty
 * about the software or its performance. 
 *********************************************************************/


/* 
 * C code for generating randomozied grid problems...
 */





#include <stdlib.h>
#include <stdio.h>
#include <sys/timeb.h>






/* data structures ... (ha ha)
 */
typedef unsigned char Bool;
#define TRUE 1
#define FALSE 0



/* helpers
 */
void create_random_positions( void );
void print_open_locked( void );
void print_key_positions( void );
void print_key_goal_positions( void );



/* command line
 */
void usage( void );
Bool process_command_line( int argc, char *argv[] );
Bool setup_key_numbers( int vec );
Bool setup_lock_numbers( int vec );




/* globals
 */

/* command line params
 */
int gx, gy, gnum_keytypes, gkey_vec, *gkey_number, glock_vec, *glock_number, gp_goal;

/* random values
 */
int gx_pos, gy_pos, **gx_key_pos, **gy_key_pos, **gx_lock_pos, **gy_lock_pos;
int **gx_key_goal_pos, **gy_key_goal_pos;

/* helper
 */
Bool **glock;



int main( int argc, char *argv[] )

{

  int x, y, i, j;

  /* seed the random() function
   */
  struct timeb tp;
  ftime( &tp );
  srandom( tp.millitm );


  /* command line treatment, first preset values
   */
  gx = -1;
  gy = -1;
  gnum_keytypes = -1;
  gkey_vec = -1;
  glock_vec = -1;
  gp_goal = 100;

  if ( argc == 1 || ( argc == 2 && *++argv[0] == '?' ) ) {
    usage();
    exit( 1 );
  }
  if ( !process_command_line( argc, argv ) ) {
    usage();
    exit( 1 );
  }

  create_random_positions();

  /* now output problem in PDDL syntax
   */
  printf("\n\n\n");

  /* header
   */
  printf("(define (problem grid-x%d-y%d-t%d-k%d-l%d-p%d)",
	 gx, gy, gnum_keytypes, gkey_vec, glock_vec, gp_goal);
  printf("\n(:domain grid)");

  printf("\n(:objects ");
  for ( y = 0; y < gy; y++ ) {
    printf("\n        ");
    for ( x = 0; x < gx; x++ ) {
      printf("f%d-%df ", x, y);
    }
  }
  printf("\n        ");
  for ( i = 0; i < gnum_keytypes; i++ ) {
    printf("shape%d ", i);
  }
  for ( i = 0; i < gnum_keytypes; i++ ) {
    if ( gkey_number[i] == 0 ) continue;
    printf("\n        ");
    for ( j = 0; j < gkey_number[i]; j++ ) {
      printf("key%d-%d ", i, j);
    }
  }
  printf("\n)");

  printf("\n(:init");
  printf("\n(arm-empty)");
  for ( y = 0; y < gy; y++ ) {
    for ( x = 0; x < gx; x++ ) {
      printf("\n(place f%d-%df)", x, y);
    }
  }
  for ( i = 0; i < gnum_keytypes; i++ ) {
    printf("\n(shape shape%d)", i);
  }
  for ( i = 0; i < gnum_keytypes; i++ ) {
    for ( j = 0; j < gkey_number[i]; j++ ) {
      printf("\n(key key%d-%d)", i, j);
      printf("\n(key-shape key%d-%d shape%d)", i, j, i);
    }
  }
  for ( y = 0; y < gy; y++ ) {
    for ( x = 0; x < gx-1; x++ ) {
      printf("\n(conn f%d-%df f%d-%df)", x, y, x+1, y);
    }
  }
  for ( y = 0; y < gy-1; y++ ) {
    for ( x = 0; x < gx; x++ ) {
      printf("\n(conn f%d-%df f%d-%df)", x, y, x, y+1);
    }
  }
  for ( y = 0; y < gy; y++ ) {
    for ( x = 1; x < gx; x++ ) {
      printf("\n(conn f%d-%df f%d-%df)", x, y, x-1, y);
    }
  }
  for ( y = 1; y < gy; y++ ) {
    for ( x = 0; x < gx; x++ ) {
      printf("\n(conn f%d-%df f%d-%df)", x, y, x, y-1);
    }
  }
  print_open_locked();
  print_key_positions();
  printf("\n(at-robot f%d-%df)", gx_pos, gy_pos);
  printf("\n)");

  printf("\n(:goal");
  printf("\n(and");
  print_key_goal_positions();
  printf("\n)");
  printf("\n)");

  printf("\n)");

  printf("\n\n\n");

  exit( 0 );

}
  
  









/* random problem generation functions
 */






void create_random_positions( void )

{

  int MAX;
  int i, j, rx, ry, r;

  MAX = -1;
  for ( i = 0; i < gnum_keytypes; i++ ) {
    if ( MAX == -1 || gkey_number[i] > MAX ) {
      MAX = gkey_number[i];
    }
    if ( glock_number[i] > MAX ) {
      MAX = glock_number[i];
    }
  }
  gx_key_pos = ( int ** ) calloc( gnum_keytypes, sizeof( int * ) );
  gy_key_pos = ( int ** ) calloc( gnum_keytypes, sizeof( int * ) );
  gx_lock_pos = ( int ** ) calloc( gnum_keytypes, sizeof( int * ) );
  gy_lock_pos = ( int ** ) calloc( gnum_keytypes, sizeof( int * ) );
  gx_key_goal_pos = ( int ** ) calloc( gnum_keytypes, sizeof( int * ) );
  gy_key_goal_pos = ( int ** ) calloc( gnum_keytypes, sizeof( int * ) );
  for ( i = 0; i < gnum_keytypes; i++ ) {
    gx_key_pos[i] = ( int * ) calloc( MAX, sizeof( int ) );
    gy_key_pos[i] = ( int * ) calloc( MAX, sizeof( int ) );
    gx_lock_pos[i] = ( int * ) calloc( MAX, sizeof( int ) );
    gy_lock_pos[i] = ( int * ) calloc( MAX, sizeof( int ) );
    gx_key_goal_pos[i] = ( int * ) calloc( MAX, sizeof( int ) );
    gy_key_goal_pos[i] = ( int * ) calloc( MAX, sizeof( int ) );
  }
  glock = ( Bool ** ) calloc( gx, sizeof( Bool * ) );
  for ( i = 0; i < gx; i++ ) {
    glock[i] = ( Bool * ) calloc( gy, sizeof( Bool ) );
    for ( j = 0; j < gy; j++ ) {
      glock[i][j] = FALSE;
    }
  }

  for ( i = 0; i < gnum_keytypes; i++ ) {
    for ( j = 0; j < glock_number[i]; j++ ) {
      while ( TRUE ) {
	rx = random() % gx;
	ry = random() % gy;
	if ( !glock[rx][ry] ) break;
      }
      glock[rx][ry] = TRUE;
      gx_lock_pos[i][j] = rx;
      gy_lock_pos[i][j] = ry;
    }
  }
  for ( i = 0; i < gnum_keytypes; i++ ) {
    for ( j = 0; j < gkey_number[i]; j++ ) {
      rx = random() % gx;
      ry = random() % gy;
      gx_key_pos[i][j] = rx;
      gy_key_pos[i][j] = ry;
    }
  }
  for ( i = 0; i < gnum_keytypes; i++ ) {
    for ( j = 0; j < gkey_number[i]; j++ ) {
      r = random() % 100;
      if ( r >= gp_goal ) {
	gx_key_goal_pos[i][j] = -1;
	gy_key_goal_pos[i][j] = -1;
	continue;
      }
      rx = random() % gx;
      ry = random() % gy;
      gx_key_goal_pos[i][j] = rx;
      gy_key_goal_pos[i][j] = ry;
    }
  }
  while ( TRUE ) {
    rx = random() % gx;
    ry = random() % gy;
    if ( !glock[rx][ry] ) break;
  }
  gx_pos = rx;
  gy_pos = ry;

}









/* printing fns
 */


  






void print_open_locked( void )

{

  int x, y, i, j;

  for ( y = 0; y < gy; y++ ) {
    for ( x = 0; x < gx; x++ ) {
      if ( !glock[x][y] ) {
	printf("\n(open f%d-%df)", x, y);
      }
    }
  }

  for ( i = 0; i < gnum_keytypes; i++ ) {
    for ( j = 0; j < glock_number[i]; j++ ) {
      printf("\n(locked f%d-%df)",
	     gx_lock_pos[i][j], gy_lock_pos[i][j]);
      printf("\n(lock-shape f%d-%df shape%d)",
	     gx_lock_pos[i][j], gy_lock_pos[i][j], i);
    }
  }

}



void print_key_positions( void )

{

  int i, j;

  for ( i = 0; i < gnum_keytypes; i++ ) {
    for ( j = 0; j < gkey_number[i]; j++ ) {
      printf("\n(at key%d-%d f%d-%df)", i, j, 
	     gx_key_pos[i][j], gy_key_pos[i][j]);
    }
  }

}



void print_key_goal_positions( void )

{

  int i, j;

  for ( i = 0; i < gnum_keytypes; i++ ) {
    for ( j = 0; j < gkey_number[i]; j++ ) {
      if ( gx_key_goal_pos[i][j] == -1 ) continue;
      printf("\n(at key%d-%d f%d-%df)", i, j, 
	     gx_key_goal_pos[i][j], gy_key_goal_pos[i][j]);
    }
  }

}








/* command line functions
 */










void usage( void )

{

  printf("\nusage:\n");

  printf("\nOPTIONS   DESCRIPTIONS\n\n");
  printf("-x <num>    x scale (minimal 1)\n");
  printf("-y <num>    y scale (minimal 1)\n\n");
  printf("-t <num>    num different key+lock types (minimal 1)\n\n");
  printf("-k <num>    number keys vector (dezimal)\n");
  printf("-l <num>    number locks vector (dezimal)\n\n");
  printf("-p <num>    probability of any key being mentioned in the goal (preset: %d)\n\n",
	 gp_goal);

}



Bool process_command_line( int argc, char *argv[] )

{

  char option;

  while ( --argc && ++argv ) {
    if ( *argv[0] != '-' || strlen(*argv) != 2 ) {
      return FALSE;
    }
    option = *++argv[0];
    switch ( option ) {
    default:
      if ( --argc && ++argv ) {
	switch ( option ) {
	case 'x':
	  sscanf( *argv, "%d", &gx );
	  break;
	case 'y':
	  sscanf( *argv, "%d", &gy );
	  break;
	case 't':
	  sscanf( *argv, "%d", &gnum_keytypes );
	  break;
	case 'p':
	  sscanf( *argv, "%d", &gp_goal );
	  break;
	case 'k':
	  sscanf( *argv, "%d", &gkey_vec );
	  if ( gnum_keytypes == -1 ) {
	    break;
	  } else {
	    if ( setup_key_numbers( gkey_vec ) ) {
	      break;
	    } else {
	      printf("\n\ncannot interpret key number vector.\n\n");
	      exit( 1 );
	    }
	  }
	  break;
	case 'l':
	  sscanf( *argv, "%d", &glock_vec );
	  if ( gnum_keytypes == -1 ) {
	    break;
	  } else {
	    if ( setup_lock_numbers( glock_vec ) ) {
	      break;
	    } else {
	      printf("\n\ncannot interpret lock number vector.\n\n");
	      exit( 1 );
	    }
	  }
	  break;
	default:
	  printf( "\n\nunknown option: %c entered\n\n", option );
	  return FALSE;
	}
      } else {
	return FALSE;
      }
    }
  }

  if ( gx < 1 ||
       gy < 1 ||
       gnum_keytypes < 1 ) {
    return FALSE;
  }

  return TRUE;

}



Bool setup_key_numbers( int vec )

{

  int current, i;

  if ( gnum_keytypes < 1 ) return FALSE;

  gkey_number = ( int * ) calloc( gnum_keytypes, sizeof( int ) );

  current = vec;

  for ( i = gnum_keytypes - 1; i >= 0; i-- ) {
    gkey_number[i] = ( int ) (current % 10);
    if ( gkey_number[i] < 0 ) return FALSE;
    current = ( int ) (current/10);
  }
  
  return TRUE;

}



Bool setup_lock_numbers( int vec )

{

  int current, i;

  if ( gnum_keytypes < 1 ) return FALSE;

  glock_number = ( int * ) calloc( gnum_keytypes, sizeof( int ) );

  current = vec;

  for ( i = gnum_keytypes - 1; i >= 0; i-- ) {
    glock_number[i] = ( int ) (current % 10);
    if ( glock_number[i] < 0 ) return FALSE;
    current = ( int ) (current/10);
  }
  
  return TRUE;

}
