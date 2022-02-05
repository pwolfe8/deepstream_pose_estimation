// Filter Pose Keypoints per Person

#include <string.h>
#include <vector>
#include <stdio.h>

template <class T>
using Vec1D = std::vector<T>;

template <class T>
using Vec2D = std::vector<Vec1D<T>>;

template <class T>
using Vec3D = std::vector<Vec2D<T>>;

class PoseFilter
{
public:
  int area_threshold;
  int frame_w;
  int frame_h;

  PoseFilter() : PoseFilter(3264, 2464) {}
  PoseFilter(int frame_w, int frame_h) : last_person_valid(false),
                                         last_largest_area(0)
  {
    // area_threshold = frame_w * frame_h / (8*8); // 1/8 w * 1/8 h
    area_threshold = frame_w * frame_h / (6 * 6); // 1/5 w * 1/5 h
  }
  ~PoseFilter() {}

  bool process_new_keypoints(Vec3D<int> people_keypoints)
  {
    // returns false if no people in frame, otherwise process
    if (people_keypoints.size() > 0)
    {
      return filter_largest_person(people_keypoints); // return true if biggest person meets area threshold reqs
    }
    else
    {
      return false;
    }
  }

  Vec1D<int> getLargestCenter()
  {
    return last_largest_person_keypoints[17];
  }

  bool filter_largest_person(Vec3D<int> people_keypoints)
  {
    int max_idx = 0;
    int max_area = 0;
    for (int i = 0; i < people_keypoints.size(); i++)
    {
      int person_area_pixels = calc_bounding_rectangle_area(people_keypoints[i]);
      if (person_area_pixels > max_area)
      {
        max_area = person_area_pixels;
        max_idx = i;
      }
    }

    // filter based on area
    if (max_area > area_threshold)
    {
      last_largest_area = max_area;
      last_largest_person_keypoints = people_keypoints[max_idx];
      std::cout << "max area: " << max_area << ", "
                << "threshold: " << area_threshold << ", ";
      // valid if they have a valid neck keypoint
      last_person_valid = (last_largest_person_keypoints[17][0] != -1);
    }
    else
    {
      last_person_valid = false;
    }

    return last_person_valid;
  }

  int calc_bounding_rectangle_area(Vec2D<int> person_keypoints)
  {
    // initialize, assuming upper left is 0,0
    int left_x = 999999;
    int right_x = 0;
    int top_y = 999999;
    int bot_y = 0;

    for (Vec1D<int> coord : person_keypoints)
    {
      int x = coord[0];
      int y = coord[1];
      if (x == -1 || y == -1)
      {
        continue;
      }

      if (x < left_x)
      {
        left_x = x;
      }
      if (x > right_x)
      {
        right_x = x;
      }
      if (y < top_y)
      {
        top_y = y;
      }
      if (y > bot_y)
      {
        bot_y = y;
      }
    }
    int area = (right_x - left_x) * (bot_y - top_y);
    // std::cout << "area: " << area << ", ";
    return area;
  }

private:
  bool last_person_valid;
  int last_largest_area;
  Vec2D<int> last_largest_person_keypoints;
};
