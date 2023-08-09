#define N 10000000
#define K 4
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

//Struct that defines a point
typedef struct Point {
    float x;
    float y;
    int cluster;
} Point;

//Struct that defines a Cluster
typedef struct Cluster {
    int size;
    Point newCentroid;
    Point centroid;
} Cluster;

clock_t start;
clock_t end;
Point *points;
Cluster *clusters;
int iterations = 0;


static inline float distance(Point p1, Point p2) {
    //No need for the actual value of the sitance. We can avoid the sqrt() function since we'll only be comparing which one is the shortest distance.
    return ((p2.x - p1.x)*(p2.x - p1.x)) + ((p2.y - p1.y)*(p2.y - p1.y));
}

void initialize () {
    points = (Point*)malloc(N*sizeof(Point));
    clusters = (Cluster*)malloc(K*sizeof(Cluster));

    srand(10);
    //Random values for the points
    for(int i = 0; i < N; i++) {
        points[i].x = (float) rand() / RAND_MAX;
        points[i].y = (float) rand() / RAND_MAX;
    }
    for(int i = 0; i < K; i++) {  
        clusters[i].centroid.x = points[i].x;
        clusters[i].centroid.y = points[i].y;
    }
}

void k_means() {
    int ready = 0;
    while(ready < K) {
        //Each iteration resets the cluster
        for (int i = 0; i < K; i++) {
            clusters[i].size = 0;
            clusters[i].newCentroid.x = clusters[i].newCentroid.y = 0.0;
        }

        //Goes through every point and compares the distance between the point and the other clusters.
        for (int i = 0; i < N; i++) {
            int clusterIndex = 0;
            float smallerDist = distance(clusters[0].centroid, points[i]);
            for (int j = 1; j < K; j++) {
                float tempDist = distance(clusters[j].centroid, points[i]);
                if (tempDist < smallerDist) {
                    smallerDist = tempDist;
                    clusterIndex = j;
                }
            }
            //Assigns point to the closest cluster.
            //Sums the value of the point to the newCentroid variable.
            clusters[clusterIndex].size++;
            points[i].cluster = clusterIndex;
            clusters[clusterIndex].newCentroid.x += points[i].x;
            clusters[clusterIndex].newCentroid.y += points[i].y;
        }
        ready = 0;
        // Checks if the newCentroid is the same as the current centroid (stopping case).
        //Sets the current centroid to the value of the newCentroid.
        for(int i = 0; i < K; i++) {
            clusters[i].newCentroid.x /= clusters[i].size;
            clusters[i].newCentroid.y /= clusters[i].size;
            if (clusters[i].newCentroid.x == clusters[i].centroid.x && 
                clusters[i].newCentroid.y == clusters[i].centroid.y) {
                ready++;
            }
            else {
                clusters[i].centroid.x = clusters[i].newCentroid.x;
                clusters[i].centroid.y = clusters[i].newCentroid.y;
            }
        }
        //Restarts the loop in case a solution hasn't been found.
        if(ready < K)
            iterations++;
    }
    //Stops the clock.
    end = clock();
}

void printEndMessage() {
    printf("\nN: %d, K = %d\n", N, K);
    for (int i = 0; i < K; i++) {
        printf("Center: (%.3f, %.3f) : size: %d\n", clusters[i].centroid.x, clusters[i].centroid.y, clusters[i].size);
    }
    printf("Iterations: %d\n", iterations);
    printf("Execution time: %fs\n\n", ((double) (end - start)) / CLOCKS_PER_SEC);
}

int main () {
    start = clock();
    initialize();
    k_means();
    printEndMessage();
    return 0;
}