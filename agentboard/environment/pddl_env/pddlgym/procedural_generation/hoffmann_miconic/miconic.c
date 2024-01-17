



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
 * C code for generating random  #floors   #passengers   miconic problems.
 *
 * mixed   mode:   user specifies probabilities for passengers being of any type
 *
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

/* random problem generation
 */
void create_random_types( void );
void create_random_journeys( void );
void create_random_no_access_facts( void );

Bool is_up_down( int p );
Bool is_vip( int p );
Bool is_going_nonstop( int p );
Bool is_attendant( int p );
Bool is_never_alone( int p );
Bool is_con_A( int p );
Bool is_con_B( int p );
Bool is_no_access( int p );

/* printing
 */
void print_all_type_lists( void );
void print_no_access_facts( void );

/* command line
 */
void usage( void );
Bool process_command_line( int argc, char *argv[] );




/* globals
 */

/* command line params
 */
int gfloors, gpassengers;
int gp_up_down, gp_vip, gp_going_nonstop;
int gp_attendant, gp_never_alone, gp_con_A, gp_con_B;
int gp_no_access, gp_no_access_floors;

/* lists of types; passengers are those that have not been assigned any
 * special type.
 */
int *gpassenger, *gup_down, *gvip, *ggoing_nonstop;
int *gattendant, *gnever_alone, *gcon_A, *gcon_B;
int *gno_access, **gno_access_floors, *gnum_no_access_floors;
int gnum_passenger, gnum_up_down, gnum_vip, gnum_going_nonstop;
int gnum_attendant, gnum_never_alone, gnum_con_A, gnum_con_B;
int gnum_no_access;

/* final random journeys
 */
int *gorigin, *gdestin;





int main( int argc, char *argv[] )

{

  int i, j;

  /* seed the random() function
   */
  struct timeb tp;
  ftime( &tp );
  srandom( tp.millitm );


  /* command line treatment, first preset all values
   */
  gfloors = -1;
  gpassengers = -1;

  gp_up_down = 0;
  gp_vip = 0;
  gp_going_nonstop = 0;
  gp_attendant = 0; 
  gp_never_alone = 0;
  gp_con_A = 0;
  gp_con_B = 0;

  gp_no_access = 0;
  gp_no_access_floors = 0;

  if ( argc == 1 || ( argc == 2 && *++argv[0] == '?' ) ) {
    usage();
    exit( 1 );
  }
  if ( !process_command_line( argc, argv ) ) {
    usage();
    exit( 1 );
  }


  /* create randomized problem;
   *
   * start by assigning types to all passengers according to
   * defined percentage values.
   */
  create_random_types();
  
  /* now design random journeys, respecting restrictions to
   * help problem becoming solvable
   */
  create_random_journeys();

  /* finally, design no access information, also due to reasonable
   * restrictions for helping problem being solvable
   */
  create_random_no_access_facts();


  /* now output problem in PDDL syntax
   */
  printf("\n\n\n");

  /* header
   */
  printf("(define (problem mixed-f%d-p%d-u%d-v%d-d%d-a%d-n%d-A%d-B%d-N%d-F%d)", 
	 gfloors, gpassengers,
	 gp_up_down, gp_vip, gp_going_nonstop, 
	 gp_attendant, gp_never_alone, gp_con_A, gp_con_B,
	 gp_no_access, gp_no_access_floors);
  printf("\n   (:domain miconic)");

  /* objects
   */
  printf("\n   (:objects ");
  /* separated this from main for the sake of clarity
   */
  print_all_type_lists();
  /* now add the floors
   */
  for ( i = 0; i < gfloors; i++ ) {
    // if ( i != 0 && i % 10 == 0 ) {
    //   printf("\n             ");
    // }
    printf("f%d ", i);
  }
  printf("- floor");
  printf(")");

  /* initial state
   */
  printf("\n\n\n(:init");
  for ( i = 0; i < gfloors - 1; i++ ) {
    for ( j = i + 1; j < gfloors; j++ ) {
      printf("\n(above f%d f%d)", i, j);
    }
    printf("\n");
  }
  printf("\n\n");
  for ( i = 0; i < gpassengers; i++ ) {
    printf("\n(origin p%d f%d)", i, gorigin[i]);
    printf("\n(destin p%d f%d)", i, gdestin[i]);
    printf("\n");
  }
  printf("\n\n");

  print_no_access_facts();

  printf("\n\n\n");
  printf("\n(lift-at f0)");
  printf("\n)");

  /* goal condition
   */
  printf("\n\n\n(:goal (and ");
  for ( i = 0; i < gpassengers; i++ ) {
    printf("\n(served p%d)", i);
  }
  printf("\n))");
  /* that's it
   */
  printf("\n)");

  printf("\n\n\n");

  exit( 0 );

}
  
  









/* random problem generation functions
 */














void create_random_types( void )

{

  int i, j, n, p;

  gnum_passenger = 0;  
  gnum_up_down = 0;
  gnum_vip = 0;
  gnum_going_nonstop = 0;
  gnum_attendant = 0; 
  gnum_never_alone = 0;
  gnum_con_A = 0;
  gnum_con_B = 0;

  gpassenger = ( int * ) calloc( gpassengers, sizeof( int ) );
  gup_down = ( int * ) calloc( gpassengers, sizeof( int ) );
  gvip = ( int * ) calloc( gpassengers, sizeof( int ) );
  ggoing_nonstop = ( int * ) calloc( gpassengers, sizeof( int ) );
  gattendant  = ( int * ) calloc( gpassengers, sizeof( int ) );
  gnever_alone = ( int * ) calloc( gpassengers, sizeof( int ) );
  gcon_A = ( int * ) calloc( gpassengers, sizeof( int ) );
  gcon_B = ( int * ) calloc( gpassengers, sizeof( int ) );

  n = ( int ) gpassengers * ( (( float ) gp_up_down) / 100.0 );
  for ( j = 0; j < n; j++ ) {
    do {
      p = random() % gpassengers;
    } while ( is_up_down( p ) );
    gup_down[gnum_up_down++] = p;
  }

  n = ( int ) gpassengers * ( (( float ) gp_vip) / 100.0 );
  for ( j = 0; j < n; j++ ) {
    do {
      p = random() % gpassengers;
    } while ( is_vip( p ) );
    gvip[gnum_vip++] = p;
  }

  n = ( int ) gpassengers * ( (( float ) gp_going_nonstop) / 100.0 );
  for ( j = 0; j < n; j++ ) {
    do {
      p = random() % gpassengers;
    } while ( is_going_nonstop( p ) );
    ggoing_nonstop[gnum_going_nonstop++] = p;
    /* it might seem that for a going going_nonstop, it's nonsense to also be
     * up_down; however, going going_nonstop only prevents the lift from STOPPING
     * at a different location than the destin. It can still move
     * up and down as often as it likes...
     *
     * therefore, do not remove a passenger from up_down once we found that
     * he also is going_nonstop
     */
  }

  n = ( int ) gpassengers * ( (( float ) gp_never_alone) / 100.0 );
  for ( j = 0; j < n; j++ ) {
    do {
      p = random() % gpassengers;
    } while ( is_never_alone( p ) );
    gnever_alone[gnum_never_alone++] = p;
  }
  /* attendant s only if there is at least one never_alone !
   */
  if ( gnum_never_alone > 0 ) {
    n = ( int ) gpassengers * ( (( float ) gp_attendant) / 100.0 );
    if ( n == 0 ) n++;/* at least one attendant */
    for ( j = 0; j < n; j++ ) {
      do {
	p = random() % gpassengers;
	/* never_alone s don't attend themselves ! */
      } while ( is_attendant( p ) ||
		is_never_alone( p ) );
      gattendant[gnum_attendant++] = p;
    }
  }

  /* now desing conflict groups; here also, a passenger can not belong to
   * both.
   */
  n = ( int ) gpassengers * ( (( float ) gp_con_A) / 100.0 );
  for ( j = 0; j < n; j++ ) {
    do {
      p = random() % gpassengers;
    } while ( is_con_A( p ) );
    gcon_A[gnum_con_A++] = p;
  }
  /* B s only if there is at least one A !
   */
  if ( gnum_con_A > 0 ) {
    n = ( int ) gpassengers * ( (( float ) gp_con_B) / 100.0 );
    for ( j = 0; j < n; j++ ) {
      do {
	p = random() % gpassengers;
	/* no member of both groups */
      } while ( is_con_B( p ) || 
		is_con_A( p ) );
      gcon_B[gnum_con_B++] = p;
    }
  }

  /* collect untyped passengers
   */
  for ( i = 0; i < gpassengers; i++ ) {
    if ( is_up_down( i ) ) continue;
    if ( is_vip( i ) ) continue;
    if ( is_going_nonstop( i ) ) continue;
    if ( is_attendant( i ) ) continue;
    if ( is_never_alone( i ) ) continue;
    if ( is_con_A( i ) ) continue;
    if ( is_con_B( i ) ) continue;
    gpassenger[gnum_passenger++] = i;
  }

}



void create_random_journeys( void )

{

  int i, j;

  gorigin = ( int * ) calloc( gpassengers, sizeof( int ) );
  gdestin = ( int * ) calloc( gpassengers, sizeof( int ) );

  for ( i = 0; i < gpassengers; i++ ) {
    /* set the origin ...
     */
    while( TRUE ) {
      gorigin[i] = random() % gfloors;
      /* no conflict A s AND B s at the same origin floor
       */
      if ( is_con_A( i ) ) {
	for ( j = 0; j < i; j++ ) {
	  if ( gorigin[j] == gorigin[i] &&
	       is_con_B( j ) ) break;
	}
	if ( j < i ) continue;
      }
      if ( is_con_B( i ) ) {
	for ( j = 0; j < i; j++ ) {
	  if ( gorigin[j] == gorigin[i] &&
	       is_con_A( j ) ) break;
	}
	if ( j < i ) continue;
      }
      /* also, do not put conflict people together with vip s to the
       * same origin or destin floor: in both cases, the lift is
       * forced to take in a conflict person, and might have to stop
       * at a floor where a different conflict person might be waiting...
       */
      if ( is_con_A( i ) ||
	   is_con_B( i ) ) {
	for ( j = 0; j < i; j++ ) {
	  if ( ( gorigin[j] == gorigin[i] ||
		 gdestin[j] == gorigin[i] ) &&
	       is_vip( j ) ) {
	    break;
	  }
	}
	if ( j < i ) continue;
      }
      /* no other constraints for origin floors ... ?
       */
      break;
    }

    /* set the destin ...
     */
    while( TRUE ) {
      gdestin[i] = random() % gfloors;
      /* do not move to the same floor ...
       */
      if ( gdestin[i] == gorigin[i] ) continue;
      /* no going_up s together with going_down s
       */
      if ( is_up_down( i ) ) {
	for ( j = 0; j < i; j++ ) {
	  if ( !is_up_down( j ) ) continue;
	  if ( ( gorigin[j] < gdestin[j] &&
		 gorigin[i] > gdestin[i] ) ||
	       ( gorigin[j] > gdestin[j] &&
		 gorigin[i] < gdestin[i] ) ) {
	    break;
	  }
	}
	if ( j < i ) continue;
      }
      /* at the destin of a vip, no never_alone should be waiting:
       * the lift does then not always have a chance to collect an attendant
       * before stopping at that location.
       */
      if ( is_vip( i ) ) {
	for ( j = 0; j < i; j++ ) {
	  if ( gorigin[j] == gdestin[i] &&
	       is_never_alone( j ) ) {
	    break;
	  }
	}
	if ( j < i ) continue;
      }
      /* also, no conflict person in the vip's destin: do not force the lift
       * to take in conflicts.
       */
      if ( is_vip( i ) ) {
	for ( j = 0; j < i; j++ ) {
	  if ( gorigin[j] == gdestin[i] &&
	       ( is_con_A( j ) || is_con_B( j ) ) ) {
	    break;
	  }
	}
	if ( j < i ) continue;
      }
      /* if he is going going_nonstop, then he is forced to move to the
       * same destin as any other going_nonstop with the same origin
       * floor.
       */
      if ( is_going_nonstop( i ) ) {
	for ( j = 0; j < i; j++ ) {
	  if ( is_going_nonstop( j ) ) break;
	}
	if ( j < i ) {
	  gdestin[i] = gdestin[j];
	  break;
	}
      }
      /* no other constraints for destin floors ... ?
       */
      break;
    }
  }

}



void create_random_no_access_facts( void )

{

  int i, j, k, p, n, pp;

  gno_access = ( int * ) calloc( gpassengers, sizeof( int ) );
  gno_access_floors = ( int ** ) calloc( gpassengers, sizeof( int * ) );
  gnum_no_access_floors = ( int * ) calloc( gpassengers, sizeof( int ) );
  for ( i = 0; i < gpassengers; i++ ) {
    gno_access_floors[i] = ( int * ) calloc( gfloors, sizeof( int ) );
    gnum_no_access_floors[i] = 0;
  }
  gnum_no_access = 0;

  n = ( int ) gpassengers * ( (( float ) gp_no_access) / 100.0 );
  for ( j = 0; j < n; j++ ) {
    do {
      p = random() % gpassengers;
    } while ( is_no_access( p ) );
    gno_access[gnum_no_access++] = p;
  }

  for ( i = 0; i < gnum_no_access; i++ ) {
    p = gno_access[i];
    for ( j = 0; j < gfloors; j++ ) {
      pp = random() % 100;
      if ( pp >= gp_no_access_floors ) continue;
      /* access to origin and destin must be allowed, of course.
       */
      if ( gorigin[p] == j ||
	   gdestin[p] == j ) {
	continue;
      }
      /* persons in origins or destins of vips shall have
       * access to all dests of vips; they will likely be moved there
       * anyway.
       */
      for ( k = 0; k < gpassengers; k++ ) {
	if ( k == p || !is_vip( k ) ) continue;
	if ( gorigin[p] == gorigin[k] ||
	     gorigin[p] == gdestin[k] ) break;
      }
      if ( k < gpassengers ) {
	for ( k = 0; k < gpassengers; k++ ) {
	  if ( k == p || !is_vip( k ) ) continue;
	  if ( gdestin[k] == j ) break;
	}
	if ( k < gpassengers ) continue;
      }
      /* attendants shall have access to all locations where never_alone s
       * are waiting
       */
      if ( is_attendant( p ) ) {
	for ( k = 0; k < gpassengers; k++ ) {
	  if ( is_never_alone( k ) &&
	       gorigin[k] == j ) break;
	}
	if ( k < gpassengers ) continue;
      }
      /* no other constraints for no access floors ... ?
       */
      gno_access_floors[i][gnum_no_access_floors[i]++] = j;
    }
  }

}



Bool is_up_down( int p )

{

  int i;

  for ( i = 0; i < gnum_up_down; i++ ) {
    if ( gup_down[i] == p ) return TRUE;
  }

  return FALSE;

}



Bool is_vip( int p )

{

  int i;

  for ( i = 0; i < gnum_vip; i++ ) {
    if ( gvip[i] == p ) return TRUE;
  }

  return FALSE;

}



Bool is_going_nonstop( int p )

{

  int i;

  for ( i = 0; i < gnum_going_nonstop; i++ ) {
    if ( ggoing_nonstop[i] == p ) return TRUE;
  }

  return FALSE;

}



Bool is_attendant( int p )

{

  int i;

  for ( i = 0; i < gnum_attendant; i++ ) {
    if ( gattendant[i] == p ) return TRUE;
  }

  return FALSE;

}



Bool is_never_alone( int p )

{

  int i;

  for ( i = 0; i < gnum_never_alone; i++ ) {
    if ( gnever_alone[i] == p ) return TRUE;
  }

  return FALSE;

}



Bool is_con_A( int p )

{

  int i;

  for ( i = 0; i < gnum_con_A; i++ ) {
    if ( gcon_A[i] == p ) return TRUE;
  }

  return FALSE;

}



Bool is_con_B( int p )

{

  int i;

  for ( i = 0; i < gnum_con_B; i++ ) {
    if ( gcon_B[i] == p ) return TRUE;
  }

  return FALSE;

}



Bool is_no_access( int p )

{

  int i;

  for ( i = 0; i < gnum_no_access; i++ ) {
    if ( gno_access[i] == p ) return TRUE;
  }

  return FALSE;

}













/* printing functions
 */













void print_all_type_lists( void )

{

  int i;
  Bool hit;

  /* passengers without any special type
   */
  if ( gnum_passenger ) {
    for ( i = 0; i < gnum_passenger; i++ ) {
 //      if ( i != 0 && i % 10 == 0 ) {
	// printf("\n             ");
 //      }
      printf("p%d ", gpassenger[i]);
    }
    printf("- passenger");
    printf("\n             ");
  }

  /* passengers that are either going_up or going_down
   */
  if ( gnum_up_down ) {
    hit = FALSE;
    for ( i = 0; i < gnum_up_down; i++ ) {
 //      if ( i != 0 && i % 10 == 0 ) {
	// printf("\n             ");
 //      }
      if ( gorigin[gup_down[i]] < gdestin[gup_down[i]] ) {
	printf("p%d ", gup_down[i]);
	hit = TRUE;
      }
    }
    if ( hit ) {
      printf("- going_up");
      printf("\n             ");
    }
    hit = FALSE;
    for ( i = 0; i < gnum_up_down; i++ ) {
 //      if ( i != 0 && i % 10 == 0 ) {
	// printf("\n             ");
 //      }
      if ( gorigin[gup_down[i]] > gdestin[gup_down[i]] ) {
	printf("p%d ", gup_down[i]);
	hit = TRUE;
      }
    }
    if ( hit ) {
      printf("- going_down");
      printf("\n             ");
    }
  }

  /* vip s
   */
  if ( gnum_vip ) {
    for ( i = 0; i < gnum_vip; i++ ) {
      if ( i != 0 && i % 10 == 0 ) {
	printf("\n             ");
      }
      printf("p%d ", gvip[i]);
    }
    printf("- vip");
    printf("\n             ");
  }

  /* going going_nonstop s
   */
  if ( gnum_going_nonstop ) {
    for ( i = 0; i < gnum_going_nonstop; i++ ) {
      if ( i != 0 && i % 10 == 0 ) {
	printf("\n             ");
      }
      printf("p%d ", ggoing_nonstop[i]);
    }
    printf("- going_nonstop");
    printf("\n             ");
  }

  /* attendant s
   */
  if ( gnum_attendant ) {
    for ( i = 0; i < gnum_attendant; i++ ) {
      if ( i != 0 && i % 10 == 0 ) {
	printf("\n             ");
      }
      printf("p%d ", gattendant[i]);
    }
    printf("- attendant");
    printf("\n             ");
  }

  /* never alone s
   */
  if ( gnum_never_alone ) {
    for ( i = 0; i < gnum_never_alone; i++ ) {
      if ( i != 0 && i % 10 == 0 ) {
	printf("\n             ");
      }
      printf("p%d ", gnever_alone[i]);
    }
    printf("- never_alone");
    printf("\n             ");
  }

  /* conflict A s
   */
  if ( gnum_con_A ) {
    for ( i = 0; i < gnum_con_A; i++ ) {
      if ( i != 0 && i % 10 == 0 ) {
	printf("\n             ");
      }
      printf("p%d ", gcon_A[i]);
    }
    printf("- conflict_A");
    printf("\n             ");
  }

  /* conflict B s
   */
  if ( gnum_con_B ) {
    for ( i = 0; i < gnum_con_B; i++ ) {
      if ( i != 0 && i % 10 == 0 ) {
	printf("\n             ");
      }
      printf("p%d ", gcon_B[i]);
    }
    printf("- conflict_B");
    printf("\n             ");
  }

}



void print_no_access_facts( void )

{

  int i, j;

  for ( i = 0; i < gnum_no_access; i++ ) {
    for ( j = 0; j < gnum_no_access_floors[i]; j++ ) {
      printf("\n(no-access p%d f%d)",
	     gno_access[i], gno_access_floors[i][j] );
    }
  }

}










/* command line functions
 */










void usage( void )

{

  printf("\nusage:\n");

  printf("\nOPTIONS   DESCRIPTIONS\n\n");
  printf("-f <num>    number of floors (minimal 2)\n");
  printf("-p <num>    number of passengers (minimal 1)\n\n");

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
	case 'f':
	  sscanf( *argv, "%d", &gfloors );
	  break;
	case 'p':
	  sscanf( *argv, "%d", &gpassengers );
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

  if ( gfloors < 2 ||
       gpassengers < 1 ) {
    return FALSE;
  }

  return TRUE;

}

