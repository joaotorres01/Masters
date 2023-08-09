#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


float *points_x;
float *points_y;
int *cluster;

float *centroid_x;
float *centroid_y;

float *newCentroid_x;
float *newCentroid_y;

int *size;

int iterations = 0;
int N=0;
int K=0;


static inline float distance(float p1_x, float p1_y, float p2_x, float p2_y) {
    //No need for the actual value of the distance. We can avoid the sqrt() function since we'll only be comparing which one is the shortest distance.
    return ((p2_x - p1_x)*(p2_x - p1_x)) + ((p2_y - p1_y)*(p2_y - p1_y));
}


void initialize(){
    points_x = (float *)malloc(N * sizeof(float));
    points_y = (float *)malloc(N * sizeof(float));
    cluster = (int *)malloc(N * sizeof(int));

    centroid_x = (float *)malloc(K * sizeof(float));
    centroid_y = (float *)malloc(K * sizeof(float));

    newCentroid_x = (float *)malloc(K * sizeof(float));
    newCentroid_y = (float *)malloc(K * sizeof(float));
    size = (int *)malloc(K * sizeof(int));


    srand(10);
    // Random values for the points
    for (int i = 0; i < N; i++){
        points_x[i] = (float)rand() / RAND_MAX;
        points_y[i] = (float)rand() / RAND_MAX;
    }
    for (int i = 0; i < K; i++){
        centroid_x[i] = points_x[i];
        centroid_y[i] = points_y[i];
    }
}

void k_means(){
    for(iterations = 0; iterations < 20; iterations++) {
        // Each iteration resets every cluster
        #pragma omp parallel for
        for (int i = 0; i < K; i++){
            size[i] = 0;
            newCentroid_x[i] = 0.0;
            newCentroid_y[i] = 0.0;
        }

        // Goes through every point and compares the distance between the point and the other clusters.
        float smallerDist;
        int clusterIndex;
        #pragma omp parallel for private(smallerDist, clusterIndex)
        for (int i = 0; i < N; i++){
            smallerDist = distance(centroid_x[0], centroid_y[0], points_x[i], points_y[i]);
            clusterIndex = 0;
            for (int j = 1; j < K; j++){
                float tempDist = distance(centroid_x[j], centroid_y[j], points_x[i], points_y[i]);
                clusterIndex = tempDist < smallerDist ? j : clusterIndex;
                smallerDist = tempDist < smallerDist ? tempDist : smallerDist;
            }
            //Stores cluster index associated to each point
            cluster[i] = clusterIndex;
        }

        for (int i = 0; i < N; i++) {
            // Assigns point to the closest cluster.
            // Sums the value of the point to the newCentroid variable.
            size[cluster[i]]++;
            newCentroid_x[cluster[i]] += points_x[i];
            newCentroid_y[cluster[i]] += points_y[i];
        }

        // Checks if the newCentroid is the same as the current centroid (stopping case).
        // Sets the current centroid to the value of the newCentroid.
        for (int i = 0; i < K; i++){
            newCentroid_x[i] /= size[i];
            newCentroid_y[i] /= size[i];
            centroid_x[i] = newCentroid_x[i];
            centroid_y[i] = newCentroid_y[i];
        }
    }
}

static inline void printEndMessage(){
    printf("\nN: %d, K = %d\n", N, K);
    for (int i = 0; i < K; i++){
        printf("Center: (%.3f, %.3f) : size: %d\n", centroid_x[i], centroid_y[i], size[i]);
    }
    printf("Iterations: %d\n", iterations);
}

int main(int argc, char *argv[]){

    if (argc == 3) 
        argv[3] = "1";

    if(argc<3){
        printf("Usage: ./k_means <number of points> <number of clusters> <number of threads> \n");
        return -1;
    }

    N=atoi(argv[1]);
    K=atoi(argv[2]);
    omp_set_num_threads(atoi(argv[3]));
    
    initialize();
    k_means();
    printEndMessage();
    return 0;
}